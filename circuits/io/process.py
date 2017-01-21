"""Process

This module implements a wrapper for basic ``subprocess.Popen`` functionality.
"""
from io import BytesIO
from subprocess import PIPE, Popen

from circuits import BaseComponent, Event, handler
from circuits.core.manager import TIMEOUT

from .events import close, started, write
from .file import File


class terminated(Event):
    """terminated Event

    This Event is sent when a process is completed

    :param args:  (process)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        super(terminated, self).__init__(*args)


class Process(BaseComponent):

    channel = "process"

    def init(self, args, cwd=None, shell=False):
        self.args = args
        self.cwd = cwd
        self.shell = shell

        self.p = None
        self.stderr = BytesIO()
        self.stdout = BytesIO()

        self._status = None
        self._terminated = False

        self._stdout_closed = False
        self._stderr_closed = False

        self._stdin = None
        self._stderr = None
        self._stdout = None

        self._stdin_closed_handler = None
        self._stderr_read_handler = None
        self._stdout_read_handler = None
        self._stderr_closed_handler = None
        self._stdout_closed_handler = None

    def start(self):
        self.p = Popen(
            self.args,
            cwd=self.cwd,
            shell=self.shell,
            stdin=PIPE,
            stderr=PIPE,
            stdout=PIPE
        )

        self.stderr = BytesIO()
        self.stdout = BytesIO()

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
            handler("read", channel=self._stderr.channel)(
                lambda self, data: self.stderr.write(data)
            )
        )

        self._stdout_read_handler = self.addHandler(
            handler("read", channel=self._stdout.channel)(
                lambda self, data: self.stdout.write(data)
            )
        )

        self._stderr_closed_handler = self.addHandler(
            handler("closed", channel=self._stderr.channel)(
                lambda self: setattr(self, '_stderr_closed', True)
            )
        )

        self._stdout_closed_handler = self.addHandler(
            handler("closed", channel=self._stdout.channel)(
                lambda self: setattr(self, '_stdout_closed', True)
            )
        )

        self.fire(started(self))

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
        self.fire(write(data), "{0:d}.stdin".format(self.p.pid))

    @property
    def status(self):
        if getattr(self, "p", None) is not None:
            return self.p.poll()

    @handler("generate_events")
    def _on_generate_events(self, event):
        if self.p is not None and self._status is None:
            self._status = self.p.poll()

        if self._status is not None and self._stderr_closed \
                and self._stdout_closed and not self._terminated:
            self._terminated = True
            self.removeHandler(self._stderr_read_handler)
            self.removeHandler(self._stdout_read_handler)
            self.removeHandler(self._stderr_closed_handler)
            self.removeHandler(self._stdout_closed_handler)

            self.fire(terminated(self))
            self.fire(close(), self._stdin.channel, self._stdout.channel, self._stderr.channel)

            event.reduce_time_left(0)
            event.stop()
        else:
            event.reduce_time_left(TIMEOUT)
