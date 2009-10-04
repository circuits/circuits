from __future__ import with_statement
# Package:  app
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Application Components

This package contains components useful for building and deploying applications.
"""

import os
import sys

from circuits import Component

class Daemon(Component):

    def __init__(self, pidfile, path="/", stdin="/dev/null", stdout="/dev/null",
            stderr="/dev/null"):
        super(Daemon, self).__init__()

        self._pidfile = pidfile
        self._path = path
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr

    def _writepid(self):
        with open(self._pidfile, "w") as f:
		    f.write(str(os.getpid()))

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
	    os.chdir(path)
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
	    si = open(os.path.abspath(os.path.expanduser(stdin)), "r")
	    so = open(os.path.abspath(os.path.expanduser(stdout)), "a+")
	    se = open(os.path.abspath(os.path.expanduser(stderr)), "a+", 0)
	    os.dup2(si.fileno(), sys.stdin.fileno())
	    os.dup2(so.fileno(), sys.stdout.fileno())
	    os.dup2(se.fileno(), sys.stderr.fileno())

    def started(self, manager, mode):
        if not manager == self and mode is None:
            self._daemonize()
            self._writepid()
