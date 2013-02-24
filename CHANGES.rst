circuits-2.1.0 20130224 (<release>)
-----------------------------------


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
- Rewrite test_filer unit test.
  Ensured EOF event is not triggered for files opened in a or + modes.
- Added simple examples demonstrating circuits' primitives
- Added example of .fire(...) primitive
- Restructured circuits.io and implemented circuits.io.Process with unit test
- Forgot to add test_process unit test
- Added Hello World example
- Fixed event handler for generate_events
- Implemented multiprocessing support with communication via full duplex pipes. 
  Fixed worker processes and added unit test
- Made components started in process mode not link by default.
  Have to explicitly set the kwarg link=True
- Fixed process pools and added unit test
- Fixed name of method for handling inotify events -
  conflicting with ._process of Manager/Component
- Renamed ._process to .__process so as to not conflict with Worker
- Fixed raising of SystemExit or KeyboardInterrupt
- Trying to fix sending/receiving of events and their values
- Fixed IPv6 address evaluation.
- WebSockets reimplemented as specified by RFC 6455.
- Modified the way caching works with the Statis dispatcher
  and serve_file(...) function. Set Last-Modified instead of a
  large Expires header.
- Marked as a Missing Feature - still being worked on.
- Brought back the ``circuits.core.bridge.Bridge``.
  With it better inter-process communications via high-speed full duplex pipes
  using ``circuits.net.sockets.Pipe`` (UNIX Only), a much simpler API.
  
  In addition, a chnage to the way Value Notification works. .notify of an
  event instance can either be True or a channel to send the ValueChanged
  event to.
- Causes errors. Wrong thing to do here.
- Use uuid4 for worker channels.
- Removed left over debugging code
- Added capability of components started in proces mode to
  link to artbritrary managers other than themselves (if link=True)
- Added unit test for testing a component in process mode linked with
  another parent system separately
- Added timers examples ressurected from old circuits
- Thread safety for watcher
- Reverts test_component_targeting.py
- Fixed Connection header interpretation.
- Updated documentation for WebSocket.
- Changed the way process linking works by not starting the parent in
  thread mode.
- Fixes watcher test fixture
- Implemented .handlers() and re-implemented .handles(). [Delivers #41573841]
- Removed superfluous bridge test
- Fixed usage of .start starting Workers in process mode
- Better internal variable name
- Start worked either when the system starts or we are
  regsitered to an already started system
- Implemented .handlers() correctly
- Set unique channels for the Pipe and Bridge when briding processes
- Removed. Going to reimplement all this
- Don't cause a nastry fork bomb\!
- Marked test_process_pool as skipping XXX: Broken Functionality
- Fixed sleeping when nothing to do adding needs_resume logic to the pollers
- Proposed new Worker Component -- wrapping multiprocessing.Process
- Accidentla commit
- Trying to re-implement Pool...
- Marked some tests as broken
- Added support for both Process and Thread in Worker component with same API.
- Reverted changes to the task handler for Worker
- Removed .resume()
- Fixed some brokeness in future
- Trying to make @future work with Worker in process mode
- Lock bench
- Switches worker to apply_async
- Allow the poller to sleep when tasks are running
- Use ThreadPool for worker threads
- Cleaned up Worker
- benchmark only branch
- Removed pool - covered by worker
- Workaround for Threadpool bug started from secondary threads
- Fixed dispatchers return value.
- Firing Connect event when a web socket connection is established to make
  behavior look even more like ordinary sockets.
- Restored 2.0.1 GenerateEvents handling with minor enhancements to get
  things working again.
- Nuked @future decotator due to pickling problems for processes.
- Unmarked test as failing. Test now passes prefectly
- Allow coroutine-style tasks to terminate the system
  via raise of SystemExit or KeyboardINterrupt
- Fixed SSL support for circuits.web [Delivers #42007509]
- Dropping events unnoticed when waiting is definitely a bad idea. Fixed.
- Clarification on implementing a GenerateEvents handler.
- Added missing import (timed wait with FallBackGenerator cannot have
  worked for some time).
- Optimized GenerateEvents handling.
- Backed out of changeset 3413:98d0056ef18a
- Optimized management of FallbackGenerator.
- Fixed a problem with events being out of sequence when _fire is called
  recursively. The fix exposes a problem with conftest.Waiter
  (events getting lost because they are produced too fast,
  therefore queue is increased). Reducing production rate will be in
  next commit.
- Small fix for new event queue handling.
- Fixed problem with handler cache update and concurrent event
  handling/structure changes. This happens e.g. in unit tests when the
  app is started and the test program adds or removes components concurrently.
- Optimized/clarified GenerateEvents implementation.
- One more concurrency problem fixed.
- Fixed generate events handler.
- Fixed bug with handler cache being always invalidated.
  Avoid stop() acting as concurrent thread on _dispatcher().
- Added unit test for url quoting of static files for the static
  circuits.web dispatcher. [Delivers #41882655]
- Added unit test for secure circutis.web server. [Delivers #42849393]
- Fixed creation/registration/location of poller upon startup or registration
- Skip test_secure_server if ssl is not available
- Fixed payload length calculation in web sockets protocol.
- Some very small - but measurable - performance improvements.
  Checking them in mainly because now no one else needs to think
  about whether they have an effect.
- Fixed conflicting attribute.
- Added new .pid property to Manager fixing tests.core.test_bridge
  - Broken by 70677b69bf05
- Fixed ipv6 socket tests for OSX and badly configured IPv6 networks
- Ugly fix for this test
- Fixed ready handler for test_node
- For some reason removing max_events in the Watcher fixture for esting
  purposes fixes some tests on OSX
- Small sample to hopefully test for memory leaks :)
- Improved .handlers() to recursively return handlers of it's subclasses
  whilst filtering out private handlers (_.*)
- Use BaseComponent for convenience for non-handler methods
- Return a list of all handlers except handlers listneing to private events
- Left over print - oops :)
- Moved to examples/
- Re-added an old revived example of an IRC Client integrating the urwid
  curses library for the interface
- Improved comment.
- Added multi-add support for Gateway web compnoent [Delivers #40071339]
- Fixed Python 3 compatibility for retrieving the .resumse() method.
  Fixes Issue #35
- Removed unused StringIO import
- A bunch of Python 3.1 compatibility fixes (mostly import fixes)
- Added an example of using yield to perform cooperative multi-tasking
  inside a request event handler
- Uses echo for test_process
- Fixes process stdout/stderr handling
  Process was not waiting for all output from a process to have been
  processed and resulted sometimes some of the process output being lost
  while stopping.
- A bunch more Python 3 fixes. Using the six module here.
- Added a fall back error handler, so problems aren't discarded
  silently any more.
- Ooops accidently committed this
- Fixed some Python 3 import issues
- More Python 3 fixes
- Fixed Python 3 issue with iterators
- Use range for Python 3 compatibility
- Fixed assertions for Python 3 compat
- Accidently commited a test with Debugger
- Fixed value_changed handler to check correctly for binary types
  (Python 3 fixes)
- Python 3 fixes for string type checks
- Refactored for Python 3
- More Python 3 fixes. Marked the rest as Broken on Python 3
- Fixed broken web tests for Python 3 by wrapping the request
  body in a TextIOWrapper for FieldStorage
- Fixed XML and JSON RPC Dispatchers for Python 3
- Replace .has_key() with in for Python 3 compatibility
- Fixed a TypeError being raised in the request handler for websockets
  dispatcher
- Prevent the underlying TCPClient connect handler from inadvertently
  being triggered by connec events being fired to the web client
- Unmarked as skipping. No longer broken on Python 3
- Finished cleaning up my code base.
- Removed some debugging junk I had forgotten to get rid of.
- Fixed File for Python 3 support adding optional encoding support
- Fixed Process for Python 3
- Ooops :/
- Fixed test_logger_Error for Python 3
- Fixed Bridge for Python 3
- Fixed Node for Python 3
- Added pytest.PYVER and Marked test_secure_server web test as Broken
  on Python 3.2 (needs fixing)
- Marked a bunch of 3.2 and 3.3 specific tests that are broken with
  these versions (needs looking into)
- Removed Broken on Python 3 marked - these tests now pass on 3.1 3.2 and 3.3
- Fixed SSL Sockets for Python 3.2/3.3 (Should do_handshake()
  be executed in a thread?)
- Added tox configuration file. Just run: run
- Configure tox to output junitxml
- Fixed tox configuration
- Assuming localhost was incorrect. Sorry Mark :/
- Fixed test_logger for pypy
- Backed out changeset 7be64d8b6f7c
- Reconfigured tox settings
- Hopefully fixed tox.ini to detect jenkins
- Fixed tox.ini to work on jenkins (can't seem to auto detect jenkins :/)
- Added tox config for checking documetnation
- Changed the output filename of xml resutls for docs env (tox)
- Added pytest-cov as a dep to the docs env (tox)
- Configured coverage to output xml output
- Removed ptest-cov dep from docs env (tox)
- Trying to fix the randomly failing test_node test.
- Ooops broke wait_for - fixed hopefully
- Backed out changeset 795712654602
- Backed out changeset 1ee04d5fb657
- Added ignore for generated junitxml output files
- Hopefully an improved unit test for node using the manager and watcher
  fixtures.
- Updated with supported version of Python
- Fixed the logic of path -> wsgi dispatching in Gateway
- Fixed an awful bug with wrappers.Response whereby
  a default Content-Type was always set regardless and didn't allow
  anything else to set this.
- Fixed test_disps so it doesn't use an existing port that's in use.
- Added a missing piece of WSGI 1.0 functionality for wsgi.Gateway
  -- The write() callable
- Write bytes in this test
- Correctly handle unicode (I think)
- Fixed a bug with null responses from WSGI Applications
  hosted by wsgi.Gateway. Empty class did not implement __nonzero__
  for Python 2.x [Delivers #43287263]
- Remvoed pyinotify dep from tox config so Windows tests can run
- Skip test_unixserver for Windows
- Skip this test on Windows
- Skip these tests on Windows
- Skip this test on Windows
- Fixed test_tcp_bind for Windows
- Updated docs and re-added FAQ from old wiki
  (updated slightly) [Delivers #43389199]
- Fixed bottom of FAQ
- Updated Change Log [#42945315]
- Updated Release Notes [#42945315]
- Fixed list of new changes for 2.1.0 release notes
- Updated Developet Docs
- Bumped version to 2.1.0
- More resource efficient timer implementation [Delivers #43700669].
- Fixed a problem with cLength being unknown if self.body == False.
- Test fails on shining panda py32 only. May be a race condition
  (wait_for using same loop interval as timer interval).
  Checking in for testing.
- Fixed problem with "Content-Length: 0" header not being generated for
  empty responses.
- Backed out of changeset 3575:ece3ee5472ef, makes CI hang for unknown reason.
- Hopefully finally fixed problems with timer test on CI platform.
- Updated pypi classifier for circuits
- Fixed random problems with opening SSL socket.
- Fixed concurrence problem (doing reset() in event loop and calling unregister() concurrently).
- Modified test a bit to find out what happens in CI environment
  (problem not reproducible in local py32).
- Calling headers.setdefault twice for the same name doesn't make sense.
- Adapted test case to previous fix.
- Fixed problem with "Content-Length: 0" header not being generated
  for empty responses.
- Fixed insecure usage of class variable.
- Reverted to old timer implementation. Cannot find bug in new version
  that only occurs in CI/py32 environment (cannot be reproduced locally).
- Make sure that check runs faster than timer increments.
- Added missing Content-Length header (must be present according to RFC 2616).
- Provide a more informative representation.
- Fixed a docstring typo
- Just re-raise the exception here rather than hide it with
  an InternalServer exception
- Potential failing test for [#43885227]
- Fixed problem with receiving incomplete header data (first chunk doesn't
  already include empty line that separates headers and body).
- Fixed problem with header not being detected if a chunk ends exactly after
  \r\n of last header line and next chunk starts with empty line (\r\n)
  before body.
- Fixes inconsisent semantic behavior in channel selection.
- Fixed expression for _handler_channel in Manager.getHandlers(...)
- Fixed (and simplified) handler_channel evaluation.
- Fixed channel representation for cases where channel is a component.
- Adapted prepare_unregister_complete handling to fixed semantics for
  using managers as channels.
- Notifications are to be signaled to the given manager.
  Now that using managers as channels works properly, it showed that hey
  never were.
- Value change notifications are fired using Value's manager as channel,
  so mke sure to listen on that.
- Value's notifications are fired on its manager component
  -- by default the component that fired the event the value belongs to.
  Moved handler to proper place (is better place anyway).
- Encoding is necessary for this to succeed on py3.2
  (urllib2 there doesn't accept body of type str).
- Added missing files to manifest. [Delivers #44650895] (Closes Issue #36)
- Fixing encoding problems.
- Fixing py2/py3 problem by using bytearray as abviously the only
  common denominator.
- multipart/form-data is binary. Boundaries are ASCII,
  but data between boundaries may be anything (depending on part's header)
- Trying to fix unicode issues
- Marked test_node as Broken on Windows - Pickling Error with thread.lock
- Trying to fix broken unit test on Windows
- Setup docs with Google Analyitics
- Marked test_tcp_connect_closed_port(...) as Broken on Windows
  -- Need to fix this; this test is a bit weird :/
- Marked test_tcp_reconnect(...) test as Broken on Windows
- Updated state of test_tcp_reconnect(...) test on Windows
  -- Apparently only Broken on Windows on Python 3.2 (odd)
- Fixed TypeError
- Marked as Broken on pypy
  -- For some reason we're getting \x00 (null bytes)
  in the stream when using the Python std lib logger.
- Marked tests.core.test_debugger.test_filename(...) as Broken on pypy
  -- Need to investigate this
- Updated support platforms to include pypy
