Release Notes
-------------

.. _Issue #14: https://bitbucket.org/prologic/circuits/issue/14

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

- circuits.app: Fixed `Issue #14`_.

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

