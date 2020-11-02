"""Serial I/O

This module implements basic Serial (RS232) I/O.
"""
from collections import deque

from circuits.core import Component, Event, handler
from circuits.core.pollers import BasePoller, Poller
from circuits.core.utils import findcmp
from circuits.six import binary_type
from circuits.tools import tryimport

from .events import close, closed, error, opened, read, ready

serial = tryimport("serial")

TIMEOUT = 0.2
BUFSIZE = 4096


class _open(Event):

    """_open Event"""


class Serial(Component):

    channel = "serial"

    def __init__(self, port, baudrate=115200, bufsize=BUFSIZE,
                 timeout=TIMEOUT, encoding='UTF-8', readline=False, channel=channel):
        super(Serial, self).__init__(channel=channel)

        if serial is None:
            raise RuntimeError("No serial support available")

        self._port = port
        self._baudrate = baudrate
        self._bufsize = bufsize
        self._encoding = encoding
        self._readline = readline

        self._serial = None
        self._poller = None
        self._buffer = deque()
        self._closeflag = False

    @handler("ready")
    def _on_ready(self, component):
        self.fire(_open(), self.channel)

    @handler("_open")
    def _on_open(self, port=None, baudrate=None, bufsize=None):
        self._port = port or self._port
        self._baudrate = baudrate or self._baudrate
        self._bufsize = bufsize or self._bufsize

        self._serial = serial.Serial(
            port=self._port, baudrate=self._baudrate, timeout=0)
        self._fd = self._serial.fileno()  # not portable!

        self._poller.addReader(self, self._fd)

        self.fire(opened(self._port, self._baudrate))

    @handler("registered", "started", channel="*")
    def _on_registered_or_started(self, component, manager=None):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self.fire(ready(self))
            else:
                if component is not self:
                    return
                component = findcmp(self.root, BasePoller)
                if component is not None:
                    self._poller = component
                    self.fire(ready(self))
                else:
                    self._poller = Poller().register(self)
                    self.fire(ready(self))

    @handler("stopped", channel="*")
    def _on_stopped(self, component):
        self.fire(close())

    @handler("prepare_unregister", channel="*")
    def _on_prepare_unregister(self, event, c):
        if event.in_subtree(self):
            self._close()

    def _close(self):
        if self._closeflag:
            return

        self._poller.discard(self._fd)

        self._buffer.clear()
        self._closeflag = False
        self._connected = False

        try:
            self._serial.close()
        except EnvironmentError:
            pass

        self.fire(closed())

    def close(self):
        if not self._buffer:
            self._close()
        elif not self._closeflag:
            self._closeflag = True

    def _read(self):
        try:
            if self._readline:
                data = self._serial.readline(self._bufsize)
            else:
                data = self._serial.read(self._bufsize)
            if not isinstance(data, binary_type):
                data = data.encode(self._encoding)

            if data:
                self.fire(read(data)).notify = True
        except (OSError, IOError) as exc:
            self.fire(error(exc))
            self._close()

    def _write(self, data):
        try:
            if not isinstance(data, binary_type):
                data = data.encode(self._encoding)

            try:
                nbytes = self._serial.write(data)
            except serial.SerialTimeoutException:
                nbytes = 0
            if nbytes < len(data):
                self._buffer.appendleft(data[nbytes:])
        except (OSError, IOError) as e:
            self.fire(error(e))
            self._close()

    def write(self, data):
        if self._poller is not None and not self._poller.isWriting(self._fd):
            self._poller.addWriter(self, self._fd)
        self._buffer.append(data)

    @handler("_disconnect")
    def __on_disconnect(self, sock):
        self._close()

    @handler("_read")
    def __on_read(self, sock):
        self._read()

    @handler("_write")
    def __on_write(self, sock):
        if self._buffer:
            data = self._buffer.popleft()
            self._write(data)

        if not self._buffer:
            if self._closeflag:
                self._close()
            elif self._poller.isWriting(self._fd):
                self._poller.removeWriter(self._fd)
