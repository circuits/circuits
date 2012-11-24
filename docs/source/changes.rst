:tocdepth: 2

.. _changes:

ChangeLog
=========


.. include:: ../../CHANGES


circuits-2.0.0 20121122 (cheetah)
---------------------------------

- Fixed circuits.web entry point
- Fixed `tools.reprhandler()` for compatibility with Python-3.3
- Added ``*channels`` support to waitEvent
- Added example of using .call
- Fixed logic around firing the Daemonize event when registering this component during run-time and after start-up
- Fixed use of reprhandler
- Fixed listening channel for exceptions/errors.
- Fixed channels for Log event.
- Fixed config loading. Fire a Ready event when the Environment is completely ready.
- Added .items(...) method to Config component.
- Added BaseEvent, LiteralEvent, DerivedEvent to the core and circuits name-spaces
- Fixed IRC protocol
- Added has_option to Config component
- Avoid error if user un-registers a component twice.
- Fixed base_url for WebConsole
- Fixed bug with sending Response for a Expect: 100-continue (Closes issue #32)
- Added a new circuits.web test that ensures that large posts > 1024 bytes work
- Updated conf so that doc can be built even if circuits isn't installed
- Updated reference of guide to howtos
- Updated man headers so that they weren't all "Components"
- Fixed all web dispatcher tests
- Fixed XMLRPC dispatcher. Must have a higher priority than the "default" dispatcher in order to coexist with it.
- Fixed unit test for failure response from web *component* (component's handler must have higher priority than default dispatcher if default dispatcher exists). 
- Added failure test for web *controller*.
- Fixed JSON dispatcher. Must have a higher priority than the "default" dispatcher in order to coexist with it.
- Fixed vpath traversal. vpath created in reverse ("test_args/1/2/3" became "3/2/1/test_args").
- Fixed evaluation of the Complete event: exclude events fired by other threads during event processing from the set of events to be tracked.
- Don't call tick on components that are waiting to be unregistered.
- Using new PrepareUnregister event to reliably remove sockets from poller.
- Fixes for PrepareUnregister and added test case.
- Added event that informs components about going to be removed from the tree.
- Fixed client request generation (MUST include Host header).
- Fixed channel naming in web.Client to allow several clients (i.e. connections to web sites) to coexist in an application.
- Prevented uncameling of event names that represent web requests. Handlers can now use the last path segment unmodified as handled event's name.
- Fixed the new dispatcher with new tests
- Fixed bug in complete event generation.
- Added optional event signaling the completion of an event and everything that has been caused by it.
- Added the possibility to redirect the success events to other channels.
- Updated documentation to reflect the new "handler suspend" feature.
- Replaced web dispatcher with simpler version
- Added support for x = yield self.callEvent(...)
- Made test_main more reliable
- Removed old BaseManager from playing with GreenletManager. Fixed test_manager_repr
- Fixed the exceptions being thrown for test_eval, but the test still fails
- Added a new failing test - evaluation of promised values
- Removed superfluous .value in test_longwait
- Added support for alllowing future handlers to have a "special" event parameter just like ordinary handlers.
- Fixed test_success
- Fixed test_removeHandler
- Added support for firing Done() and Success() after all done executing.
- Fixed callEvent
- Added 2 failing tests for yield
- Implemented promises which we detect for in circuits.web in cases where an event handler yields. Also only fire _success events after an event is well and truly finished (in the case of yielding event handlers)
- Fixed a bug with value not being set
- Fixed Issue #26
- Added capability of waiting for a specific event name on a specific channel.
- Fixed bug guarding  against tasks already removed.
- Implemented Component.init() support whereby one can define an alternative init() without needing to remember to call super(...)
- Fixed Python 3 compatibility with Unicode strings
- Added 99bottles as an example of concurrency. See: http://wiki.python.org/moin/Concurrency/99Bottles
- Removed old-style channel targeting
- Fixed and tested UDP forwarding
- Simplified udpclient example
- Implemented new version of port forwarded. TCP tested.
- Fixed Read events for UDPServer by setting .notify to True.
- Restructured the only How To Guide - Building a Simple Server
- Renamed _get_request_handler to just find_handler
- Removed channels attribute from WebEvents (fix for issue #29).
- Added Eclipse configuration files.
- Fixed uses of deprecated syntax in app.config
- Modified the defaults for channels. Set channels to event.channels, otherwise self.channel defaulting to *
- Fixed uses of deprecated syntax in env
- Fixed a bug with the Redirect event/error in circuits.web where it didn't handle Unicode strings
- fixed the web dispatcher
- Fixed test_poller_reuse test by using the now findtype() utility function
- fixed and adds tests for the web dispatcher
- Moved parseBody out into circuits.web.utils. Other code cleanup
- Added a test for a bug with the dispatcher mehere found.
- Removed itercmp() function. Added findtype() findchannel() and used better variable names. findcmp is an alias of findtype.
- Implemented optional singleton support for components
- Removed the circuits.web `routes` dispatcher as there are no tests for this and Routes dispatcher is broken - re implement at a later stage
- Removal of End feedback event
- Fixed web/test_value.py
- Fixed web futures test
- Simplified and fixed a lot of issues the circuits.bench
- Fixed circuits.web's exceptions tests and handling of exceptions.
- Fixed a potential bug with ``circuits.web.wsgi.Application``.
- Modified Manager to only assign a handler return value if it is not None.
- Fixed ``*_success`` and ``*_failure`` events fire on ``*event.channels`` so they go to the right place as expected. Fixed Issue #21
- Removed event equality test and related tests. Seems rather useless and inconsistently used
- Fixed test_gzip circuits.web test. We no longer have a Started event feedback so have to use a filter
- Fixed a corner case where one might be trying to compare an event object with a non-event object
- Fixed the event handling for circuits.web WebSockets Component by separating out the WebSockets handling from the HTTP handling (WebSocketsMediator).
- Fixed use of Value notification in circuits.web for requests.
- Fixed a bunch of examples and tests using deprecated features.
- Fixed the notify io driver and removed Debugger() from test_notify.
- Added man pages for circuits.bench, circuits.sniff and circuits.web
- Wrapped UNIX-specific calls in try/except
- Tidied up examples and removed unused imports
- removed use of coverage module in daemon test
- removed use of coverage module in signals test
- updated .push calls to .fire calls
- Fixed some deprecations warnings
- Added support for multiple webserver with different channels + tests for it
- Added support for silently ignoring  errors when writing to stderr from debugger
- Added requirements.txt file containing requirements for building docs on readthedocs.org
- Added link to Read the Docs for circuits
- Updated doc message for success event
- Fixed interrupt handler to allow ^C to be used to quit sample keyecho app
- Removed deprecated modules and functions that were deprecated 1.6
- Deleted old style event success/failure notifiers
- Fixed handling of components being added/removed when looking for ticks
- Fixed bug with ``net.Server`` .host and .port attributes.
- Deprecated ``__tick__``. Event handlers can now be specified as **tick** functions.
- Fixed handler priority inheritance to make sure we get the results in the right harder
- Fixed missing import of sys in circuits.io


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
