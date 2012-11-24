:tocdepth: 2

.. _changes:

ChangeLog
=========


.. include:: ../../CHANGES


circuits-1.6 (oceans) - 20110626
--------------------------------

- Added Python 3 support
- 80% Code Coverage
- Added optional greenlet support adding two new primitives.
  ``.waitEvent(...)`` and ``.callEvent(...)``.
- Added an example WebSockets server using circuits.web
- Added support for specifying a ``Poll`` instance to use when using the
  ``@future`` decorator to create "future" event handlers.
- Added ``add_section``, ``has_section`` and ``set`` methods to
  ``app.config.Config`` Component.
- Added support for running test suite with distutils ``python setup.py
  test``.
- Added a ``_on_signal`` event handler on the ``BaseEnvironment`` Component
  so that environments can be reloaded by listening to ``SIGHUP`` signals.
- Added support for using absolute paths in ``app.env.Environment``.
- Added support in circuits.web ``HTTP`` protocol to limit the no. of
  header fragments. This prevents OOM exploits.
- Added a ticks limit to waitEvent
- Added deprecation warnings for .push .add and .remove methods
- NEW ``Loader`` Component in ``circuits.core`` for simple plugin support.
- NEW ``app.env`` and ``app.config`` modules including a new ``app.startup``
  modules integrating a common startup for applications.
- NEW ``KQueue`` poller
- Fixed :bbissue:`17`
- Renamed ``circuits.web.main`` module to ``circuits.web.__main__`` so that
  ``python -m circuits.web`` just works.
- Fixed ``Server.host`` and ``Server.port`` properties in
  ``circuits.net.sockets``.
- Fixed :bbissue:`10`
- Fixed ``app.Daemon`` Component to correctly open the stderr file.
- Fixed triggering of ``Success`` events.
- Fixed duplicate broadcast handler in ``UDPServer``
- Fixed duplicate ``Disconnect`` event from being triggered twice on
  ``Client`` socket components.
- Removed dynamic timeout code from ``Select`` poller.
- Fixed a bug in the circuits.web ``HTTP`` protocol where headers were
  not being buffered per client.
- Fixes a missing Event ``Closed()`` not being triggered for ``UDPServer``.
- Make underlying ``UDPServer`` socket reusable by setting ``SO_REUSEADDR``
- Fixes Server socket being discarded twice on close + disconnect
- Socket.write now expects bytes (bytes for python3 and str for python2)
- Better handling of encoding in HTTP Component (allow non utf-8 encoding)
- Always encode HTTP headers in utf-8
- Fixes error after getting socket.ERRCONNREFUSED
- Allows TCPClient to bind to a specific port
- Improved docs
- Handles closing of UDPServer socket when no client is connected
- Adds an un-register handler for components
- Allows utils.kill to work from a different thread
- Fixes bug when handling "*" in channels and targets
- Fixes a bug that could occur when un-registering components
- Fixes for CPU usage problems when using circuits with no I/O pollers
  and using a Timer for timed events
