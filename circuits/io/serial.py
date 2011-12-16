# Module:   serial
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Serial I/O

This module implements basic Serial (RS232) I/O.
"""

import os
import select
from collections import deque

from circuits.core import Component
from circuits.tools import tryimport

from .events import Closed, Error, Opened, Read

serial = tryimport("serial")

TIMEOUT = 0.2
BUFSIZE = 4096


class Serial(Component):

    channel = "serial"

    def __init__(self, port, baudrate=115200, bufsize=BUFSIZE,
            timeout=TIMEOUT, channel=channel):
        super(Serial, self).__init__(channel=channel)

        if serial is None:
            raise RuntimeError("No serial support available")

        self.port = port
        self.baudrate = baudrate

        self._serial = serial.Serial()
        self._serial.port = port
        self._serial.baudrate = baudrate

        if os.name == "posix":
            self._serial.timeout = 0  # non-blocking (POSIX)
        else:
            self._serial.timeout = timeout

        self._buffer = deque()
        self._bufsize = bufsize
        self._timeout = timeout

        self._read = []
        self._write = []

        self._serial.open()
        self._fd = self._serial.fileno()

        self._read.append(self._fd)

        self.fire(Opened(self.port))

    def __tick__(self):
        r, w, e = select.select(self._read, self._write, [], self._timeout)

        if w and self._buffer:
            data = self._buffer.popleft()
            try:
                bytes = os.write(self._fd, data)
                if bytes < len(data):
                    self._buffer.append(data[bytes:])
                else:
                    if not self._buffer and self._fd in self._write:
                        self._write.remove(self._fd)
            except OSError as error:
                self.fire(Error(error))

        if r:
            data = os.read(self._fd, self._bufsize)
            if data:
                self.fire(Read(data))

    def write(self, data):
        if self._fd not in self._write:
            self._write.append(self._fd)
        self._buffer.append(data)

    def close(self):
        self._fd = None
        self._read = []
        self._write = []
        self._serial.close()
        self.fire(Closed(self.port))
