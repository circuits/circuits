Change Log
==========


1.4 (20110212)
--------------


Features
........

- circuits.core: **NEW** workers and futures modules.
  This adds thread and process concurrency support to circuits.

- circuits.web: **NEW** Web Client for circuits.web

- circuits.core: Implemented a basic handler cache on the Manager.
  Improves overall performance of circuits by as much as ~33%

- circuits.core: Passing keyword argument `sleep` to `Manager.start(...)`
  or `Manager.run(...)` is now deprecated.


Bug Fixes
.........

- circuits.app: Fixed :bbissue:`14`

- circuits.web: Fixed streaming support for `wsgi.Gateway`

- circuits.tools: Catch InvocationError from environments where pydot is
  installed but no graphviz executable (*Mac OS X*)

- circuits.web: Fixed a bug where if no "Content-Length" was provided
  (*By Google Chrom's WebSocket*) but a body was given `circuits.web`
  would expect more data to be given.

- circuits.net: Catch gaierror exceptions on calls to `gethostbyname()`
  to determine where we're binding.
  Fix for misconfigured desktop environments.

- circuits.core: Ignore `ValueError` raised if we can't install signal
  handlers such as when running as a Windows Service.

- circuits.web: Fixed -m/--multiprocessing mode and modified to accept a
  no. of processes to start (circuits.web binary/script).


1.3.3 (20110205)
----------------


Features
........

- circuits.core.workers: Add import of cpu_count/cpuCount as cpus from the
  respective multiprocessing/processing modules

- circuits.web.app: Two apps newly added. WebConsole and MemoryMonitor
  See: http://codepad.org/iQwBgfdM for an example

- circuits.core.debugger: If the Debugger isn't logging to a file or logger
  (*we're logging to sys.stderr*) it's useful to restrict the output for
  common terminal widths of 80.

  - circuits.core.debugger: Make chopping long lines when logging to sys.stderr
    optional with kwarg ``chop`` (**Default:** ``False``).

- circuits.web.errors: Make traceback available on the HTTPError Event Object
  as self.traceback


Bug Fixes
.........

- circuits.web.main: Only start multiple processes if multiprocessing is
  actually available

- circuits.core.pollers: Ignore IOError of EINTR (4)

- circuits.app: Fixed a bug with loading a Logger instance and loading the
  Config instance (*``circuits.app needs`` to be refactored*)


Examples
........

- examples/web/jsonserializer.py: New example showing how to build a simple
  request filter that intercepts the return values of request handlers before
  they get added to the response body

- examples/web/filtering.py: Fixed example


1.3.2 (20110201)
----------------


Bug Fixes
.........

- Fixed several Python 2.5 incompatibilities.

- circuits.web.wsgi: Fixed a bug with writing to the ``request.body``.
  (Forgot to rewing the ``StringIO`` instnace after writing to it)


1.3.1 (20110131)
----------------


Documentation
.............

- Fixed documentation generation


Features
........

- circuits.core.manager: Deprecated the use of the sleep parameter/argument
  in ``Manager.start(...)`` and ``Manager.run(...)`` in favor of sleeping
  for the specified ``circuits.core.manager.TIMEOUT`` when/iif there are no
  tick functions to process (eg: Timer, pollers, etc)

  -- If aftering processing **Tick Functions** there are no resulting
     events to process then a sleep will occur for ``circuits.core.TIMEOUT``
     seconds.

- circuits.core.Manager: Call ``self.stop`` right at the end of normal
  termination for script-like systems (eg: examples/cat.py)

- circuits.core.Manager: If a KeyboardInterrupt or SystemExit exception
  is raised during a **Tick Function**, then re-raise it.


Bug Fixes
.........

- circuits.web.http: Fixed a bug with HTTP streaming

- circuits.io: Fixed exceptions not being caught during shutdown

- tests.core.test_bridge: Fixed and passing again :)

- circuits.web.wsgi: Fixed a bug discovered when trying to deploy a
  circuits.web WSGI Application using the uwsgi server. In the case of
  an empty request body from the client being passed thorugh uwsgi to
  circuits.web - No Content-Length would be provided, but also any attempt
  to read from wsgi.input would block causing uwsgi to timeout
