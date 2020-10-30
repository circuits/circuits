:orphan:


==========
Change Log
==========

- :release:`3.2.1 <2020-10-30>`
- :support:`-` Added support for Python 3.6, 3.7, 3.8, 3.9-dev
- :support:`152` Dropped the support for Python 2.6 and 3.x < 3.4
- :bug:`176` Generator expressions don't raise StopIteration anymore
- :feature:`-` The exception handling has been improoved
- :feature:`273` Added a `bufsize` argument to the `__init__` of BaseServer
- :bug:`270` fix TLS support for websockets (unhandled SSLWantReadError)
- :bug:`263` Improove error handling during TLS handshake
- :bug:`269` Fix error handling when TLS handshake fails
- :bug:`266` Fix python2 `str(circuits.core.values.Value())`
- :bug:`264` Improoved robustness of IRC messages
- :bug:`257` Fix WSGI component for Python 2.7 and Python 3
- :bug:`254` Fix CRLF injection in IRC protocol
- :feature:`245` IRC: enhance stripping of colors
- :feature:`249` Add `irc.utils.irc_color_to_ansi()`
- :bug:`241` Adjust `circuits.tools.graph()` to API change in `networkx`
- :feature:`240` Added `auto_add` to `circuits.io.notify`
- :feature:`231` Add support for `STOMP` protocol
- :bug:`238` Fix parsing HTTP request without headers
- :bug:`235` the `prefix` in the `Debugger` might be a `callable` now
- :feature:`233` `circuits.core.values.Value` is now `__str__` compatible with Python 2
- :feature:`212` Improves the API for session management and adds expire support
- :feature:`224` Add new HTTP status code `308 moved permanently` (:rfc:`7538`)
- :feature:`214` Implement `STARTTLS` for sockets as `event`
- :feature:`-` Add support to set additional socket options
- :bug:`198` Made pushing onto the event queue via `fire` threadsafe.
- :feature:`202` Removed `EventType` metaclass
- :bug:`-` Fixed `manager.join()`
- :bug:`202` Removed the (unused) internal cache from `EventType`.
- :feature:`168`  Add interface for selecting the websocket subprotocol
- :bug:`54` Fix a memory leak due to `on_done` handlers
- :bug:`-` Fix python3 compatibility when parsing `HTTP` request body
- :bug:`-` Fix error handling if error contains traceback instance
- :bug:`187` Fix parsing and decoding of `application/x-www-urlencoded` payloads
- :bug:`185` Fix Denial of Service socket/memory leak for not connected clients
- :bug:`184` Fix websocket data parsing if content is larger than BUFSIZE
- :bug:`170` Fix crash from deleting undefined variables
- :bug:`173` Fix the type difference between _current_thread and _flushing_thread
- :bug:`123` Fixes bug in the `complete` event
- :bug:`165` Fix `Host` HTTP header parsing when `circuits.web.Server` is bound to a `UNIX` Socket

- :release:`3.2 <2016-06-02>`
- :bug:`119` Fixed bug in ``circuits.web.url.parse_url()`` that caused a
  display issue with port bindings on ports 80 and 443.
- :release:`3.1 <2014-11-01>`
- :bug:`-` Bridge waits for event processing on the other side before proxy handler ends. Now it is possible to collect values from remote handlers in %_success event.
- :bug:`-` Rename the FallbackErrorHandler to FallbackExceptionHandler and the event it listens to to exception
- :bug:`-` Fixes optional parameters handling (client / server).
- :bug:`-` Node: add peer node: return channel name.
- :bug:`-` Node: add event firewall (client / server).
- :bug:`-` Node: fixes the event value issue.
- :bug:`-` Node: fixes event response flood.
- :bug:`-` Node: Add node examples.
- :bug:`-` Fixed import of FallBackExceptionHandler
- :bug:`-` Fixed exception handing in circuits.web
- :bug:`-` Fixed issue in brige with ommiting all but the first events sent at once
- :bug:`-` Bridge: Do not propagate no results via bridge
- :bug:`-` Bridge: Send exceptions via brige before change the exceptions weren't propagated via bridge because traceback object is not pickable, now traceback object is replaced by corresponding traceback list
- :bug:`113` Fixed bug with forced shutdown of subprocesses in Windows.
- :bug:`115` Fixed FallbackErrorHandler API Change

- :release:`3.0.1 <2014-11-01>`
- :support:`117` Fixed inconsistent top-level examples.
- :support:`96` Link to ChangeLog from README

- :release:`3.0 <2014-08-31>`
- :bug:`111 major` Fixed broken Digest Auth Test for circuits.web
- :feature:`112` Improved Signal Handling
- :bug:`109 major` Fixed ``Event.create()`` factory and metaclass.
- :feature:`108` Improved server support for the IRC Protocol.
- :bug:`107 major` Added ``__le__`` and ``__ge__`` methods to ``circuits.web.wrappers.HTTPStatus``
- :bug:`106 major` Added ``__format__`` method to circuits.web.wrappers.HTTPStatus.
- :bug:`104 major` Prevent other websockets sessions from closing.
- :feature:`103` Added the firing of a ``disconnect`` event for the WebSocketsDispatcher.
- :bug:`102 major` Fixed minor bug with WebSocketsDispatcher causing superflusous ``connect()`` events from being fired.
- :bug:`100 major` Fixed returned Content-Type in JSON-RPC Dispatcher.
- :feature:`99` Added Digest Auth support to the ``circuits.web`` CLI Tool
- :feature:`98` Dockerized circuits. See: https://docker.io/
- :bug:`97 major` Fixed ``tests.net.test_tcp.test_lookup_failure`` test for Windows
- :support:`95` Updated Developer Documentation with corrections and a new workflow.
- :feature:`94` Modified the :class:`circuits.web.Logger` to use the ``response_success`` event.
- :support:`86` Telnet Tutorial
- :bug:`47 major` Dispatcher does not fully respect optional arguments. web
- :support:`61` circuits.web documentation enhancements docs
- :support:`85` Migrate away from ShiningPanda
- :support:`87` A rendered example of ``circuits.tools.graph()``. docs
- :support:`88` Document the implicit registration of components attached as class attributes docs
- :bug:`89 major` Class attribtues that reference methods cause duplicate event handlers core
- :support:`92` Update circuitsframework.com content docs
- :support:`71` Document the value_changed event docs
- :support:`78` Migrate Change Log maintenance and build to Releases
- :bug:`91 major` Call/Wait and specific instances of events
- :bug:`59 major` circuits.web DoS in serve_file (remote denial of service) web
- :bug:`66 major` web examples jsonserializer broken web
- :support:`73` Fix duplication in auto generated API Docs. docs
- :support:`72` Update Event Filtering section of Users Manual docs
- :bug:`76 major` Missing unit test for DNS lookup failures net
- :support:`70` Convention around method names of event handlers
- :support:`75` Document and show examples of using circuits.tools docs
- :bug:`81 major` "index" method not serving / web
- :bug:`77 major` Uncaught exceptions Event collides with sockets and others core
- :support:`69` Merge #circuits-dev FreeNode Channel into #circuits
- :support:`65` Update tutorial to match circuits 3.0 API(s) and Semantics docs
- :support:`60` meantion @handler decorator in tutorial docs
- :bug:`67 major` web example jsontool is broken on python3 web
- :support:`63` typos in documentation docs
- :bug:`53 major` WebSocketClient treating WebSocket data in same TCP segment as HTTP response as part the HTTP response. web
- :bug:`62 major` Fix packaging and bump circuits 1.5.1 for @dsuch (*Dariusz Suchojad*) for `Zato <https://zato.io/>`_
- :bug:`56 major` circuits.web HEAD request send response body web
- :bug:`45 major` Fixed use of ``cmp()`` and ``__cmp__()`` for Python 3 compatibility.
- :bug:`48 major` Allow ``event`` to be passed to the decorated function (*the request handler*) for circuits.web
- :bug:`46 major` Set ``Content-Type`` header on response for errors. (circuits.web)
- :bug:`38 major` Guard against invalid headers. (circuits.web)
- :bug:`37 major` Fixed a typo in :class:`~circuits.io.file.File`


Older Change Logs
=================

For older Change Logs of previous versions of circuits please see the respective `PyPi <http://pypi.python.org/pypi>`_ page(s):

- `circuits-2.1.0 <http://pypi.python.org/pypi/circuits/2.1.0>`_
- `circuits-2.0.1 <http://pypi.python.org/pypi/circuits/2.0.1>`_
- `circuits-2.0.0 <http://pypi.python.org/pypi/circuits/2.0.0>`_
- `circuits-1.6 <http://pypi.python.org/pypi/circuits/1.6>`_
- `circuits-1.5 <http://pypi.python.org/pypi/circuits/1.5>`_
