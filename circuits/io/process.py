#!/usr/bin/python -i

from subprocess import Popen, PIPE
from circuits.core.manager import TIMEOUT

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO  # NOQA

from circuits.io import File, Write
from circuits import handler, Component, Event


class Started(Event):
    """Started Event"""


class Stopped(Event):
    """Stopped Event"""


class Start(Event):
    """Start Event"""


class Stop(Event):
    """Stop Event"""


class Signal(Event):
    """Signal Event"""


class Kill(Event):
    """Kill Event"""


class Wait(Event):
    """Wait Event"""


class Process(Component):

    channel = "process"

    def init(self, args, cwd=None, shell=False):
        self.args = args
        self.cwd = cwd
        self.shell = shell

        self.p = None
        self.stderr = StringIO()
        self.stdout = StringIO()

        self._status = None

        self._stdin = None
        self._stderr = None
        self._stdout = None

        self._stdin_closed_handler = None
        self._stderr_read_handler = None
        self._stdout_read_handler = None

    def start(self):
        self.p = Popen(
            self.args,
            cwd=self.cwd,
            shell=self.shell,
            stdin=PIPE,
            stderr=PIPE,
            stdout=PIPE
        )

        self.stderr = StringIO()
        self.stdout = StringIO()

        self._status = None

        self._stdin = File(
            self.p.stdin,
            channel="{0:d}.stdin".format(self.p.pid)
        ).register(self)

        self._stderr = File(
            self.p.stderr,
            channel="{0:d}.stderr".format(self.p.pid)
        ).register(self)

        self._stdout = File(
            self.p.stdout,
            channel="{0:d}.stdout".format(self.p.pid)
        ).register(self)

        self._stderr_read_handler = self.addHandler(
            handler("read", channel="{0:d}.stderr".format(self.p.pid))(
                self.__class__._on_stderr_read
            )
        )

        self._stdout_read_handler = self.addHandler(
            handler("read", channel="{0:d}.stdout".format(self.p.pid))(
                self.__class__._on_stdout_read
            )
        )

        self.fire(Started(self))

    def stop(self):
        if self.p is not None:
            self.p.terminate()

    def kill(self):
        self.p.kill()

    def signal(self, signal):
        self.p.send_signal(signal)

    def wait(self):
        return self.p.wait()

    def write(self, data):
        self.fire(Write(data), "{0:d}.stdin".format(self.p.pid))

    @property
    def status(self):
        if getattr(self, "p", None) is not None:
            return self.p.poll()

    @staticmethod
    def _on_stderr_read(self, data):
        self.stderr.write(data)

    @staticmethod
    def _on_stdout_read(self, data):
        self.stdout.write(data)

    @handler("generate_events")
    def _on_generate_events(self, event):
        if self.p is not None:
            status = self.p.poll()
            if status is not self._status:
                self._status = status
                self.fire(Stopped(self))
                event.reduce_time_left(0)
                return True
            else:
                event.reduce_time_left(TIMEOUT)
