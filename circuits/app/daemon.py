# Module:   daemon
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Daemon Component

Component to daemonizae a sytem into the background and detach it from it's
controlling PTY. Supports pid file writing, logging stdin, stdout and stderr
and changing the current working directory.
"""

import os
import sys

from circuits.core import handler, BaseComponent, Event

class Daemonize(Event):
    """Daemonize Event

    This event can be fired to notify the `Daemon` Component to begin the
    "daemonization" process. This event is (*by default*) used
    automatically by the `Daemon` Component in it's "started" Event
    Handler (*This behavior can be overridden*).

    Arguments: *None*
    """

class WritePID(Event):
    """"WritePID Event

    This event can be fired to notify the `Daemon` Component that is should
    retrive the current process's id (pid) and write it out to the
    configured path in the `Daemon` Component. This event (*by default*)
    is used automatically by the `Daemon` Component after the
    :class:`Daemonize`.
    """

class Daemon(BaseComponent):
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

    def __init__(self, pidfile, path="/", stdin=None, stdout=None,
            stderr=None, channel=channel):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Daemon, self).__init__(channel=channel)

        assert os.path.isabs(path), "path must be absolute"

        if os.path.isabs(pidfile):
            self._pidfile = pidfile
        else:
            self._pidfile = os.path.join(path, pidfile)

        self._path = path

        stdio_attrs = ["_stdin", "_stdout", "_stderr"]
        for i, stdio in enumerate([stdin, stdout, stderr]):
            if stdio and os.path.isabs(stdio):
                setattr(self, stdio_attrs[i], stdio)
            elif stdio:
                setattr(self, stdio_attrs[i], os.path.join(path, stdio))
            else:
                setattr(self, stdio_attrs[i], "/dev/null")

    @handler("writepid")
    def _on_writepid(self):
        f = open(self._pidfile, "w")
        f.write(str(os.getpid()))
        f.close()

    @handler("daemonize")
    def _on_daemonize(self):
        # Do first fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                raise SystemExit, 0
        except OSError, e:
            print >> sys.stderr, "fork #1 failed: (%d) %s\n" % (errno, str(e))
            raise SystemExit, 1

        # Decouple from parent environment.
        os.chdir(self._path)
        os.umask(077)
        os.setsid()

        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit second parent
                raise SystemExit, 0
        except OSError, e:
            print >> sys.stderr, "fork #2 failed: (%d) %s\n" % (e, str(e))
            raise SystemExit, 1

        # Now I am a daemon!

        # Redirect standard file descriptors.
        si = open(self._stdin, "r")
        so = open(self._stdout, "a+")
        se = open(self._stderr, "a+", 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        self.push(WritePID())

    @handler("started", filter=True, priority=100.0, target="*")
    def _on_started(self, manager, mode):
        if not manager == self and mode is None:
            self.push(Daemonize())
