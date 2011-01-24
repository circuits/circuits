# Package:  app
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Application Components

Contains various components useful for application development and tasks
common to applications.

:copyright: CopyRight (C) 2004-2011 by James Mills
:license: MIT (See: LICENSE)
"""

from __future__ import with_statement

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

    :param pidfile: .pid filename/path.
    :type  pidfile: str or unicode
    :param stdin:   stdin path     (**default:** /dev/stdin)
    :type  stdin:   str or unicode
    :param stdout:  stdout path    (**default:** /dev/stdout)
    :type  stdout:  str or unicode
    :param stderr:  stderr path    (**default:** /dev/stderr)
    :type  stderr:  str or unicode
    """

    def __init__(self, pidfile, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        channel = kwargs.get("channel", Daemon.channel)
        super(Daemon, self).__init__(channel=channel)

        self._pidfile = os.path.abspath(os.path.expanduser(pidfile))
        self._path = kwargs.get("path", "/")
        self._stdin = kwargs.get("stdin", "/dev/stdin")
        self._stdout = kwargs.get("stdout", "/dev/stdout")
        self._stderr = kwargs.get("stderr", "/dev/stderr")

    @handler("writepid")
    def _writepid(self):
        with open(self._pidfile, "w") as f:
            f.write(str(os.getpid()))

    @handler("daemonize")
    def _daemonize(self):
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
        si = open(os.path.abspath(os.path.expanduser(self._stdin)), "r")
        so = open(os.path.abspath(os.path.expanduser(self._stdout)), "a+")
        se = open(os.path.abspath(os.path.expanduser(self._stderr)), "a+", 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        self.push(WritePID())

    @handler("started", filter=True, priority=1.0, target="*")
    def _on_started(self, manager, mode):
        if not manager == self and mode is None:
            self.push(Daemonize())
