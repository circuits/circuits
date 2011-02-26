Release Notes
-------------


Code Coverage
.............

Code Coverage and Tests need a special section this release. This is
the first release where circuits now has the following coverage:

- **Python-2.6**: 77%

- **Python-2.5**: 76%

We're well on our way to 100% !!!


Features
........

- circuits.app: Revamped environment, config and logger components

- circuits.net: socket module cleanup.

  - **API Changes:**

    - Keyword argument `ssl` changed to `secure`

    - Attribute `ssl` changed to `ssl`

- circuits.app: Allow the ``Daemon`` Component to daemonize an application
  by simply registering it but only if the application is already running.

- circuits.app: Import ``Log`` Event to circuits.app namespace

- circuits.core: Cosmetic changes to poller components.
  Base Poller renamed from ``_Poller`` to ``BasePoller``

- circuits.core: Added new function ``utils.itercmp`` which returns an
  iterator that matches the given component.

- circuits.net: Added a new Event ``Closed`` for Server components
  which gets sent when the listening socket has closed.

- circuits.net: Added a ``_on_stopped`` event handler to close all
  client connections on a Server Component and close the connection on
  a Client Component when the system is terminated.

- circuits.net: Streamline ``host`` and ``port`` methods.

- circuits.web: Streamline ``host`` and ``port`` methods.

In both cases, the ``host`` attribute always returns
``socket.getsockname()[0]``

- circuits.core: Make default ``TIMEOUT`` 10ms
  This is the timeout period when we have no running **Tick Functions**.

- scripts: Added ``circuits.bench``, ``circuits.sniff`` and ``circuis.web``
  scripts which are installed by distutils. ``circuits.web`` still gets
  installed by setuptools.

- circuits.core: Add an ``on_ready`` event handler for the ``Bridge`` and
  set an attribute ``_bridge`` on the component being started in "process
  mode" so we can check whether it's ready or not via the ``ready``
  attribute on the ``Bridge`` instnace.

- Makefile: Added ``graph`` rule using snakefood and ghostscript to produce
  a PDF of the architecture of the circuits library.

- circuits.core: Make ``chop`` attribute work for when we're logging
  to a logger

- circuits.web: Set the **Content-Type** to "application/json" for all
  ``JSONController`` responses.

- circuits.web: Allow HTTP status message to be customized so implementing
  WebSockets is a little eaiser.

- circuits.web: Don't presume to add a "Content-Type" header.

- circuits.tools: Added a new helper function ``tryimport`` which given a
  list of modules to try and import and an optional message; will try to
  import each module returning the first successful one. If none of the
  modules can be improted, a warning is useed with the optional message.

- circuits.web: Restructured ``dispatchers``. ``circuits.web.dispatchers``
  is now it's own package.

- circuits.web: NEW ``WebSockets`` dispatcher.

- circuits.web: Raise a ``RuntimeError`` exception if when trying to create
  an instance of the ``JSONRPC`` dispatcher we have no "json" support.

- circuits.web: Raise a ``RuntimeError`` exception if when trying to create
  an instance of the ``Routes`` dispatcher we have no "routes" support.

- circuits.web: Added support for passing body and headers to ``Request``
  event

- circuits.web: Only close the connection if Connection header has the
  value "close" for the ``Client``.

- circuits.web: Added a _on_write event handler to ``Client`` to allow
  direct writing to the underlying transport (eg: from a WebSockets
  client).


Bug Fixes
.........

- circuits.net: Fixed a bug when if we try to initiate a connection
  on a disconnected socket (eg: TCPClient) we get EBADF or EINVAL.

- circuits.core: Fixed a bug with Event Handler Inheritence
  where overridden Event Handlers were not being picked up properly.

- circuits.core: Fixed a minor bug in ``@future`` decorator where it
  wasn't passing the correct ``channel`` and was starting non-pooled
  futures as processes instead.
