circuits-2.1.0 20130217
-----------------------


Features
........


- Added IPv6 Support [#39987887]
- Document and Comment all Examples [#40112459]
- Update WebSockets dispatcher in circuits.web [40064247]
- Component Event Handlers Property [#41573841]
- Component targeting performance [#41644031]
- Multi-App WSGI Gateway [#40071339]
- More efficient timer implementation [#43700669]


Bugs
....


- Fix the broken links in the Users page [#40063597]
- circuits.tools.inspect shows incorrect ticks [#41650961]
- Race Condition with call/wait primitives [#41643711]
- RESTful Dispatcher [#41643773]
- Fix Component instance targeting [#41644025]
- Worker Processes [#41643831]
- Make examples/web/sslserver.py work again [42007509]
- Value instance in body [43287263]


Chores
......


- Import shadowing in manager.py [#41644023]
- Run the codebase through flake8 [#41651093]
- URL Quoting Unit Test [#41882655]
- SSL Unit Test [#42849393]
- Python 3.x Support [43027337]
- Fill out FAQ in Docs [#43389199]
- Write Developer Docs [#43389193]

Other Changes
.............


A list of other changes we forgot to track :)

- Fixed latency timing for circuits.bench on win32
- Updated the URL for ReadTheDocs
- Updated the Getting Started / Downloading documentation to
  say something about the Tags tab for downloading archives.
- Removed unused import in ``circuits.app.env``
- Added some documentation about how HTTP requests are handled.
- Removed unused code
- A simple chat server implementation (Examples)
- Fixed a bug with Manager.processTasks and Error event firing.
  handler was not being set correctly
- Fixes wrong variable names in sockets.py
- Fixed an UnboundLocalError bug
- Expect the original method to be passed as input to ``Manager.removeHandler``
  ``Manager.addHandler`` now returns a reference to the original method.
- Guard against a None _sock or non-existent _sock object.
- Allow a custom host, port and secure option to be passed
  to the connect event handler of circuits.web.client.Client
- Redesigned tests/web/conftest.py with newer pytest APIs using
  ``@pytest.fixture(...)``
- Experimental new Watcher/Manager fixtures
- Docs for Fallback generator
- Removing the concept of _ticks, @tick and friends
- Fixes timers
- Reimplemented circuits.io.File as per circuits.net.sockets
- Re-implemented Notify Component and fixed test
- Reworked Notifier Component to be more async friendly
- Fixed a bug with the repr of Manager and thus Components with non-str channels. eg: (1, 1)
- Added a unit test for generate_events handler
- Fixed terminal example demonstrating Streaming with circuits.web
- Fixed index page for terminal web example
- Added an Open event to File
- Fixed a bug with the static dispatcher for circuits.web whereby
  the path was not being unquoted
- Fixed a bug with the static circuits.web dispatcher whereby directory
  listing did not quote urls
- Added simple examples demonstrating circuits' primitives
- Added example of .fire(...) primitive
- Restructured circuits.io and implemented circuits.io.Process with unit test
- Added Hello World example
- Made components started in process mode not link by default.
  Have to explicitly set the kwarg ``link=component_instance``.
- Fixed raising of ``SystemExit`` or ``KeyboardInterrupt``.
- Modified the way caching works with the Static dispatcher

- Brought back the ``circuits.core.bridge.Bridge``.
  With it better inter-process communications via high-speed full duplex pipes
  using ``circuits.net.sockets.Pipe`` (UNIX Only), a much simpler API.

  In addition, a change to the way Value Notification works. .notify of an
  event instance can either be True or a channel to send the ValueChanged
  event to.

- Added timers examples resurrected from old circuits

- Global handlers and component targeting
  Global handlers would be ignored when using component targeting.

  This patch considers them. To do this, we have added an extra property
  to managers.

  You can use traverse_children_handlers to increase performance when you have
  a huge number of components. Put the components that are only meant to be
  used with component targeting  under a single component. The hierarchy
  looks like this:

  .. code-block:: python

     Root -> Umbrella Component -> Component 1, Component 2, Component 3, ...
          -> Debugger()
          -> etc

- Set Umbrella Component traverse_children_handlers to false to prevent
  traversing the huge number of children components.
- Fixed Connection header interpretation.
- Updated documentation for WebSocket.
- Removed pool - covered by worker
- Fixed dispatchers return value.
- Firing Connect event when a web socket connection is established to make
  behavior look even more like ordinary sockets.
- Nuked ``@future`` decorator due to pickling problems for processes.
- Allow coroutine-style tasks to terminate the system via raise
  of ``SystemExit`` or ``KeyboardInterrupt``
- Dropping events unnoticed when waiting is definitely a bad idea. Fixed.
- Clarification on implementing a GenerateEvents handler.
- Optimized GenerateEvents handling.
- Optimized management of FallbackGenerator.
- Fixed a problem with events being out of sequence when _fire
  is called recursively. The fix exposes a problem with conftest.Waiter
  (events getting lost because they are produced too fast, therefore queue
  is increased). Reducing production rate will be in next commit.
- Small fix for new event queue handling.
- Fixed problem with handler cache update and concurrent event
  handling/structure changes. This happens e.g. in unit tests when the
  app is started and the test program adds or removes components concurrently.
- Optimized/clarified GenerateEvents implementation.
- One more concurrency problem fixed.
- Fixed generate events handler.
- Fixed bug with handler cache being always invalidated.
  Avoid ``stop()`` acting as concurrent thread on ``_dispatcher()``
- Fixed payload length calculation in web sockets protocol.
- Some very small - but measurable - performance improvements.
  Checking them in mainly because now no one else needs to think about
  whether they have an effect.
- Fixed IPv6 socket tests for OSX and badly configured IPv6 networks
- Fixed ready handler for test_node
- Re-added an old revived example of an IRC Client integrating
  the urwid curses library for the interface
- Added an example of using yield to perform cooperative multi-tasking
  inside a request event handler
- Uses echo for test_process

- Fixes process stdout/stderr handling
  Process was not waiting for all output from a process to have been
  processed and resulted sometimes some of the process output being lost
  while stopping.

- Added a fall back error handler, so problems aren't discarded silently
  any more.
- Fixed a TypeError being raised in the request handler for WebSockets
  dispatcher
- Prevent the underlying TCPClient connect handler from inadvertently being
  triggered by connect events being fired to the web client
- Added tox configuration file. Just run: ``tox``
- Configure tox to output junitxml
- Fixed the logic of path -> wsgi dispatching in Gateway
- Fixed an awful bug with wrappers.Response whereby a default Content-Type was
  always set regardless and didn't allow anything else to set this.
- Fixed test_disps so it doesn't use an existing port that's in use.
- Added a missing piece of WSGI 1.0 functionality for wsgi.Gateway.
  The ``write()`` callable
