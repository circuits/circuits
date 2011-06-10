Release Notes - circuits-1.6 (oceans)
-------------------------------------


Python 3 Support
................

This is the third attempt at getting Python 3 support for circuits working
while still maintaining Python 2 compatibility. These release finally adds
full support for Python 3 as well as maintaining compatibility with Python
2.6 and 2.7 with the same codebase.

.. note::
   Python 2.5 support has been dropped as of this release and will no
   longer be supported in future. There may be a maintenance branch
   specifically for Python 2.5 if required.


Code Coverage
.............

circuits now has 80% test coverage on all supported versions of Python
including Python 2.6, Python 2.7 and Python 3.2


Features
........

...


Bug Fixes
.........

...


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

- Fixed ``Server.host`` and ``Server.port`` properties in
  ``circuits.net.sockets``.

The ``Server.host`` property will reteurn what ``getsockname()`` returns
on the underlying listening socket and return it's first item if it's a
tuple, otherwise it will return the entire string (eg: a UNIX Socket).

The ``Server.port`` property does a similar thing but returns ``None``
in the case of ``getsockname()`` **not** returning a tuple.

- New ``Loader`` Component in ``circuits.core`` for simple plugin support.

- Fixed Issue #10

- Renamed ``circuits.web.main`` module to ``circuits.web.__main__`` so that
  ``python -m circuits.web`` just works.

- Fixed ``app.Daemon`` Component to correctly open the stderr file.

- circuits.core: Always trigger a ``Success`` event if no errors.

When an event handler has fired successfully and no errors have occured
always trigger a ``Success`` event so that defining the ``success``
attribute on an ``Event`` class definition makes sense.


- New ``app.env`` and ``app.config`` modules including a new ``app.startup``
  modules integrating a common startup for applications.

- New ``KQueue`` poller

- Fixed duplicate broadcast handler in ``UDPServer``


- Fixed duplicate ``Disconnect`` event from being triggered twice on
  ``Client`` socket components.

- Removed dynamic timeout code from ``Select`` poller.

This is considered broken as it does not work correctly in all cases and
causes things to hang -- especially when integrating with Naali.
Thanks Toni for identifying this!

- Fixed a bug in the circuits.web ``HTTP`` protocol where headers were
  not being buffered per client.
- Added support in circuits.web ``HTTP`` protocol to limit the no. of
  header fragments. This prevents OOM exploits.
- Fixes a missing Event ``Closed()`` not being triggered for ``UDPServer``.
- Make underlying ``UDPServer`` socket reuseable by setting ``SO_REUSEADDR``
- Fixes Server socket being discarded twice on close + disconnect
- Socket.write now expects bytes (bytes for python3 and str for python2)
- Better handling of encoding in HTTP Component (allow non utf-8 encoding)
- Always encode http headers in utf-8
- Fixes error after getting socket.ERRCONNREFUSED
- Allows TCPClient to bind to a specific port
- Addes deprecation warnings for .push .add and .remove methods
- Improved docs
- Addes a ticks limit to waitEvent
- Handles closing of udpserver socket when no client is connected
- Adds an unregister handler for components
- Allows utils.kill to work from a different thread
- Fixes bug when handling "*" in channels and targets
- Fixes a bug that could occur when unregistering components
- Fixes for CPU usage problems when using circuits with no I/O pollers
  and using a Timer for timed events
