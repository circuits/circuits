"""Daemon Component

Component to daemonize a system into the background and detach it from its
controlling PTY. Supports PID file writing, logging stdin, stdout and stderr
and changing the current working directory.
"""
from os import (
    _exit, chdir, closerange, dup2, fork, getpid, remove, setsid, umask,
)
from os.path import isabs
from resource import RLIM_INFINITY, RLIMIT_NOFILE, getrlimit
from sys import stderr, stdin, stdout

from circuits.core import Component, Event, handler


class daemonize(Event):
    """daemonize Event"""


class daemonized(Event):
    """daemonized Event"""


class deletepid(Event):
    """"deletepid Event"""


class writepid(Event):
    """"writepid Event"""


class Daemon(Component):
    """Daemon Component

    :param pidfile: .pid filename
    :type  pidfile: str or unicode

    :param stdin:   filename to log stdin
    :type  stdin:   str or unicode

    :param stdout:  filename to log stdout
    :type  stdout:  str or unicode

    :param stderr:  filename to log stderr
    :type  stderr:  str or unicode
    """

    channel = "daemon"

    def init(self, pidfile, path="/", stdin=None, stdout=None,
             stderr=None, channel=channel):

        assert isabs(path), "path must be absolute"

        self.pidfile = pidfile
        self.path = path

        self.stdin = (
            stdin if stdin is not None and isabs(stdin) else "/dev/null"
        )

        self.stdout = (
            stdout if stdout is not None and isabs(stdout) else "/dev/null"
        )

        self.stderr = (
            stderr if stderr is not None and isabs(stderr) else "/dev/null"
        )

    def deletepid(self):
        remove(self.pidfile)

    def writepid(self):
        with open(self.pidfile, "w") as fd:
            fd.write(str(getpid()))

    def daemonize(self):
        try:
            pid = fork()
            if pid > 0:
                # exit first parent
                _exit(0)
        except OSError as e:
            stderr.write(
                "fork #1 failed: {0:d} ({1:s})\n".format(
                    e.errno, str(e)
                )
            )

            raise SystemExit(1)

        # decouple from parent environment
        chdir(self.path)
        setsid()
        umask(0)

        # do second fork
        try:
            pid = fork()
            if pid > 0:
                # exit from second parent
                _exit(0)
        except OSError as e:
            stderr.write(
                "fork #2 failed: {0:d} ({1:s})\n".format(
                    e.errno, str(e)
                )
            )

            raise SystemExit(1)

        # redirect standard file descriptors
        stdout.flush()
        stderr.flush()

        maxfd = getrlimit(RLIMIT_NOFILE)[1]
        if maxfd == RLIM_INFINITY:
            maxfd = 2048

        closerange(0, maxfd)

        si = open(self.stdin, "r")
        so = open(self.stdout, "a+")
        se = open(self.stderr, "a+")

        dup2(si.fileno(), stdin.fileno())
        dup2(so.fileno(), stdout.fileno())
        dup2(se.fileno(), stderr.fileno())

        self.fire(writepid())
        self.fire(daemonized(self))

    def registered(self, component, manager):
        if component == self and manager.root.running:
            self.fire(daemonize())

    @handler("started", priority=100.0, channel="*")
    def on_started(self, component):
        if component is not self:
            self.fire(daemonize())
