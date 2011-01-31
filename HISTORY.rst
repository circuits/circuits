1.3.1 (20110131)
================

Documentation
-------------

- Fixed documentation generation

Features
--------

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
---------

- circuits.web.http: Fixed a bug with HTTP streaming

- circuits.io: Fixed exceptions not being caught during shutdown

- tests.core.test_bridge: Fixed and passing again :)

- circuits.web.wsgi: Fixed a bug discovered when trying to deploy a
  circuits.web WSGI Application using the uwsgi server. In the case of
  an empty request body from the client being passed thorugh uwsgi to
  circuits.web - No Content-Length would be provided, but also any attempt
  to read from wsgi.input would block causing uwsgi to timeout

