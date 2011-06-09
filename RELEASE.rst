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


changeset:   2404:b54e7a91b4b5
user:        jamesmills
date:        Tue Mar 22 07:07:30 2011 +0000
files:       circuits/app/__init__.py circuits/app/config.py circuits/app/env.py circuits/app/startup.py tests/app/test_config.py tests/app/test_env.py
description:
- circuits.app: New ``env`` and ``config`` modules including a new ``startup``
  modules integrating a common startup for applications.


changeset:   2405:7986570c0847
user:        jamesmills
date:        Mon Mar 28 06:36:51 2011 +1000
files:       circuits/app/env.py
description:
- circuits.app: Added priority to event handlers.


changeset:   2406:533ce7abd741
user:        jamesmills
date:        Tue Mar 29 20:54:25 2011 +1000
files:       examples/ircclient.py
description:
- Fixed "examples/ircclient.py" for Python 3


changeset:   2407:3415337af58d
branch:      py2
parent:      2400:75d72a9fd3be
user:        Osso <adeiana@gmail.com>
date:        Tue Mar 29 02:38:11 2011 +0200
files:       circuits/core/pollers.py
description:
Added KQueue poller


changeset:   2408:5244bbc674d1
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Tue Mar 29 17:57:39 2011 +0200
files:       circuits/core/pollers.py
description:
Fixes for KQueue poller


changeset:   2409:11c66688f688
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Wed Mar 30 00:40:24 2011 +0200
files:       circuits/web/__init__.py circuits/web/servers.py
description:
Web server that uses stdin/stdout instead of sockets to communicate with clients, this is used when the parent process binds the socket and gives the outpout to child processes to stdin. That setup is used for soft restarts to be able to restart child processes without closing the socket thus without losing connections


changeset:   2410:2b95959fcd76
branch:      py2
parent:      2400:75d72a9fd3be
user:        Toni Alatalo <toni@playsign.net>
date:        Thu Mar 31 10:20:17 2011 +0300
files:       examples/ircclient.py
description:
fix irc example nick collisiong handling, by adding the missing import of irc.Nick


changeset:   2411:9fe8c06d27bf
branch:      py2
parent:      2409:11c66688f688
parent:      2410:2b95959fcd76
user:        prologic
date:        Thu Mar 31 19:27:47 2011 +1000
description:
Merged with 2b95959fcd76


changeset:   2412:ed3b0842f0aa
branch:      py2
user:        prologic
date:        Thu Mar 31 19:31:33 2011 +1000
files:       circuits/web/servers.py
description:
- circuits.web: Rearracned import of ``circuits.io.stdin`` and
  ``circuits.io.stdout`` so that running tests don't fail.

py.test overrides stdin/stdout so these will not exists during testing.


changeset:   2413:311681dc8087
branch:      py2
user:        prologic
date:        Thu Mar 31 20:54:13 2011 +1000
files:       tests/web/test_websockets.py
description:
- tests.web: Disable ``test_websockets`` for Python < 2.7 as this doesn't
  work for uncompatible url parsing functionality in the std-lib.


changeset:   2414:86a44ea31cb9
branch:      py2
parent:      2409:11c66688f688
user:        Osso <adeiana@gmail.com>
date:        Wed Mar 30 00:51:31 2011 +0200
files:       circuits/core/pollers.py
description:
80 columns for KQueue poller


changeset:   2415:b65c2f2c6b09
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Wed Mar 30 02:10:47 2011 +0200
files:       tests/net/test_tcp.py tests/net/test_udp.py tests/net/test_unix.py
description:
generate tests for KQueue backend


changeset:   2416:f7fd92aed439
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Wed Mar 30 02:12:09 2011 +0200
files:       circuits/core/pollers.py
description:
assume KQueue.discard() is called by Server._close and don't call it twice, also updated to use Poller.getTarget


changeset:   2417:163131f1854f
branch:      py2
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Mar 31 11:43:09 2011 +0200
files:       circuits/core/pollers.py
description:
don't discard socket on error from KQueue poller, wait for EOF


changeset:   2418:34e98398394b
branch:      py2
parent:      2417:163131f1854f
parent:      2413:311681dc8087
user:        prologic
date:        Thu Mar 31 20:55:02 2011 +1000
description:
Merged with 311681dc8087


changeset:   2419:b31ed69ab7ca
branch:      py2
user:        jamesmills
date:        Tue Apr 05 23:10:04 2011 +0000
files:       tests/app/test_daemon.py tests/core/test_signals.py
description:
- Marked ``test_daemon`` and ``test_signal`` as "Failing..."


changeset:   2420:851e55a8ba45
branch:      py2
parent:      2412:ed3b0842f0aa
user:        prologic
date:        Fri Apr 08 09:57:14 2011 +1000
files:       circuits/net/sockets.py
description:
- circuits.net: Fixed cleaning up Client socket during write errors.


changeset:   2421:f4e654149bd2
branch:      py2
parent:      2419:b31ed69ab7ca
parent:      2420:851e55a8ba45
user:        prologic
date:        Fri Apr 08 09:59:41 2011 +1000
description:
Merged with 851e55a8ba45


changeset:   2422:12c5652203df
branch:      py2
user:        prologic
date:        Fri Apr 08 12:31:04 2011 +1000
files:       circuits/net/sockets.py
description:
- circuits.net: Fixed duplicate broadcast handler in ``UDPServer``


changeset:   2423:15f1b9e2fc4f
branch:      py2
user:        prologic
date:        Fri Apr 08 18:49:11 2011 +1000
files:       scripts/circuits.web setup.py
description:
- Fixed entrypoints for ``circuits.web``


changeset:   2424:f73a82718fb3
branch:      py2
user:        prologic
date:        Fri Apr 08 19:06:24 2011 +1000
files:       circuits/net/sockets.py
description:
- circuits.net: Only trigger a ``Disconnect`` event once

When cleaning up the ``Client`` socket, only trigger the ``Disconnect``
event once and once only.


changeset:   2425:4439b2d381dd
branch:      py2
user:        jamesmills
date:        Wed Apr 13 05:02:07 2011 +0000
files:       circuits/core/pollers.py
description:
- circuits.core: Removed dynamic timeout code from ``Select`` poller.

This is considered broken as it does not work correctly in all cases and causes things to hang -- especially when integrating with Naali. Thanks Toni for identifying this!


changeset:   2426:003a276688cc
branch:      py2
parent:      2424:f73a82718fb3
user:        prologic
date:        Wed Apr 13 19:07:45 2011 +1000
files:       circuits/__init__.py docs/source/api/circuits_core_components.rst docs/source/api/circuits_web_main.rst docs/source/conf.py docs/source/faq.rst docs/source/features.rst docs/source/features.rst.bak docs/source/foreword.rst docs/source/guides/index.rst docs/source/guides/server.py docs/source/guides/server.rst docs/source/guides/server_application.rst docs/source/index.rst docs/source/introduction.rst docs/source/start/quick.rst docs/source/tutorial.rst docs/source/tutorial/001.py docs/source/tutorial/002.py docs/source/tutorial/003.py docs/source/tutorial/004.py docs/source/tutorial/005.py docs/source/tutorial/006.py docs/source/tutorial/007.py docs/source/tutorial/index.rst docs/source/users.rst
description:
Reworking of docs


changeset:   2427:70f1c377f5d9
branch:      py2
parent:      2425:4439b2d381dd
parent:      2426:003a276688cc
user:        prologic
date:        Wed Apr 13 19:09:31 2011 +1000
files:       docs/source/features.rst docs/source/features.rst.bak docs/source/foreword.rst docs/source/guides/server_application.rst docs/source/introduction.rst docs/source/tutorial.rst
description:
Merged with 003a276688cc


changeset:   2428:f21167125c1e
branch:      py2
user:        prologic
date:        Thu Apr 14 11:10:44 2011 +1000
files:       docs/source/tutorial/008.py docs/source/tutorial/009.py docs/source/tutorial/index.rst
description:
- docs: Added two further section to the tutorial


changeset:   2429:5c0451b6c6a2
branch:      py2
user:        prologic
date:        Thu Apr 14 13:46:51 2011 +1000
files:       docs/source/tutorial/006.py docs/source/tutorial/007.py docs/source/tutorial/008.py docs/source/tutorial/009.py docs/source/tutorial/index.rst
description:
- docs: Improved some parts of the tutorial


changeset:   2430:1d12f0f5a12f
branch:      py2
user:        jamesmills
date:        Wed Apr 20 01:32:10 2011 +0000
files:       tmp/examples/dynamicweb/plugins/__init__.py tmp/examples/dynamicweb/plugins/test.py tmp/examples/dynamicweb/server.py
description:
Added an example of demonstrating the ``Loader`` Component with circuits.web


changeset:   2431:fa22cd090c11
branch:      py2
user:        jamesmills
date:        Wed Apr 20 01:38:44 2011 +0000
files:       tmp/examples/dynamicweb/server.py
description:
Improved error/result checking on recent dynamicweb examples

``Loader.load(...)`` will either raise an exception (if any Component raises
an exception during initialization or registration), or it will return None
if no components were found or the Component instance if all went well.


changeset:   2432:c3b581f86b89
parent:      2406:533ce7abd741
parent:      2431:fa22cd090c11
user:        jamesmills
date:        Wed Apr 20 02:05:23 2011 +0000
files:       circuits/__init__.py circuits/app/daemon.py circuits/core/__init__.py circuits/core/pollers.py circuits/core/utils.py circuits/net/sockets.py circuits/web/__init__.py circuits/web/__main__.py circuits/web/servers.py docs/source/features.rst docs/source/features.rst.bak docs/source/foreword.rst docs/source/guides/server_application.rst docs/source/introduction.rst docs/source/tutorial.rst examples/ircclient.py setup.py tests/app/test_daemon.py tests/core/test_signals.py tests/net/test_tcp.py tests/net/test_udp.py tests/net/test_unix.py tests/web/test_websockets.py
description:
Merged with py2


changeset:   2433:717aff03c962
branch:      py2
parent:      2431:fa22cd090c11
user:        jamesmills
date:        Wed Apr 20 02:06:12 2011 +0000
description:
Maintaining a py2 branch and making default py3 doesn't work very well -- This branch is closed.


changeset:   2434:18879701c4ad
parent:      2432:c3b581f86b89
user:        jamesmills
date:        Wed Apr 20 23:15:57 2011 +0000
files:       circuits/core/components.py circuits/core/handlers.py circuits/tools/__init__.py tests/conftest.py
description:
Fixed compatibility between Python 2.x (2.6 to 2.7) and Python 3.x (3.0 to 3.2)

.. note::
   We plan to drop support for Python 2.5 (*real soon*).


changeset:   2435:1c3817944c03
user:        jaemsmills
date:        Wed Apr 20 23:48:31 2011 +0000
files:       circuits/core/pollers.py circuits/net/sockets.py
description:
Fixed more Python 3 compatibility issues


changeset:   2436:bbc312b58fb0
branch:      py2
parent:      2424:f73a82718fb3
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 08 12:56:21 2011 +0200
files:       tests/net/test_tcp.py
description:
testing for connections on a closed port


changeset:   2437:44089e9c0c37
branch:      py2
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 08 14:31:32 2011 +0200
files:       circuits/core/values.py circuits/web/dispatchers/xmlrpc.py circuits/web/http.py
description:
set a handled member in ValueChanged for preventing HTTP component to double handle it during a XMLRPC call


changeset:   2438:171811ca2a6f
branch:      py2
user:        Alessio Deiana <adeiana@gmail.com>
date:        Mon Apr 11 16:24:02 2011 +0200
files:       circuits/web/dispatchers/xmlrpc.py
description:
give higher priority to xmlrpc dispatcher


changeset:   2439:cf1bd44a7256
branch:      py2
user:        Alessio Deiana <adeiana@gmail.com>
date:        Mon Apr 11 16:24:53 2011 +0200
files:       circuits/web/http.py
description:
buffer header per client to handle requests that don't send all header data in one packet


changeset:   2440:376657afe8bf
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 11 23:23:43 2011 +0200
files:       circuits/web/http.py
description:
limit the number of header fragments (prevent oom exploit)


changeset:   2441:0d6d66660f15
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 11 23:24:21 2011 +0200
files:       tests/web/test_http.py
description:
tests for fragmented http headers (multiple packets)


changeset:   2442:c4a403329e7a
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Tue Apr 12 02:19:03 2011 +0200
files:       circuits/web/http.py
description:
cleanup buffers when erroring on too many http fragements


changeset:   2443:b0e2955eb27e
branch:      py2
user:        Osso <adeiana@gmail.com>
date:        Tue Apr 12 03:00:24 2011 +0200
files:       circuits/web/http.py
description:
we don't have a request/response yet, so just an invalid headers error


changeset:   2444:879af3cdeaf9
parent:      2435:1c3817944c03
parent:      2443:b0e2955eb27e
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Apr 21 11:54:56 2011 +0200
files:       circuits/core/values.py circuits/web/dispatchers/xmlrpc.py circuits/web/http.py tests/net/test_tcp.py
description:
merged osso changes from py2 branch


changeset:   2445:e23e1289ea5d
branch:      py2
parent:      2443:b0e2955eb27e
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Apr 21 11:58:04 2011 +0200
description:
closed py2, now python2 and 3 both work with default


changeset:   2446:291e032d900d
parent:      2444:879af3cdeaf9
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Apr 21 14:38:56 2011 +0200
files:       circuits/web/_httpauth.py circuits/web/controllers.py circuits/web/dispatchers/virtualhosts.py circuits/web/dispatchers/websockets.py circuits/web/dispatchers/xmlrpc.py circuits/web/errors.py circuits/web/http.py circuits/web/servers.py circuits/web/utils.py circuits/web/wrappers.py
description:
fixes of various import for py2 compatibility


changeset:   2447:07d81e4ad198
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Apr 21 17:58:42 2011 +0200
files:       circuits/app/config.py circuits/net/protocols/line.py circuits/web/client.py circuits/web/servers.py tests/app/test_env.py tests/web/test_basicauth.py tests/web/test_conn.py tests/web/test_cookies.py tests/web/test_core.py tests/web/test_digestauth.py tests/web/test_exceptions.py tests/web/test_expires.py tests/web/test_expose.py tests/web/test_future.py tests/web/test_generator.py tests/web/test_json.py tests/web/test_logger.py tests/web/test_null_response.py tests/web/test_request_failure.py tests/web/test_serve_download.py tests/web/test_serve_file.py tests/web/test_servers.py tests/web/test_sessions.py tests/web/test_static.py
description:
updated imports to work with python2


changeset:   2448:462abc1bc989
user:        Alessio Deiana <adeiana@gmail.com>
date:        Thu Apr 21 18:26:08 2011 +0200
files:       circuits/web/wsgi.py tests/web/test_unicode.py tests/web/test_utils.py tests/web/test_value.py tests/web/test_web_task.py tests/web/test_wsgi_gateway.py tests/web/test_wsgi_gateway_errors.py tests/web/test_wsgi_gateway_generator.py tests/web/test_wsgi_gateway_yield.py tests/web/test_xmlrpc.py tests/web/websocket.py
description:
updated more imports to work with python2


changeset:   2449:bf9e9546767c
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 11:18:18 2011 +0200
files:       tests/conftest.py
description:
fix for wait_event in tests


changeset:   2450:2fc8c32f3c44
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 15:29:37 2011 +0200
files:       circuits/core/debugger.py tests/app/test_env.py tests/conftest.py tests/core/test_debugger.py tests/web/test_yield.py
description:
fixed tests for debugger, was import trying to write a non-unicode string into io.StringIO when using py2, now uses StringIO.StringIO if available


changeset:   2451:887667b894ce
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:04:32 2011 +0200
files:       tests/net/test_pipe.py
description:
added kqueue to net/test_pipe tests


changeset:   2452:f4e304eaeb42
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:05:19 2011 +0200
files:       tests/core/test_utils.py
description:
only delete .pyc if it exists since remove(ignore_errors=True) seems to still raise errors


changeset:   2453:d381cdc91606
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:06:06 2011 +0200
files:       tests/core/test_debugger.py
description:
removed left over print in core/test_debugger


changeset:   2454:2216c1dbd728
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:07:54 2011 +0200
files:       circuits/net/sockets.py
description:
py2 compatibility for passing a socket to Client(socket)


changeset:   2455:fb545d6fa9a0
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:08:31 2011 +0200
files:       circuits/net/sockets.py
description:
for unixclient only do init when registering itself and not other components


changeset:   2456:da043ba87de8
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 18:09:55 2011 +0200
files:       circuits/core/values.py
description:
py2 compatibility for Value.__iter__


changeset:   2457:9b39acd88f82
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri Apr 22 19:48:22 2011 +0200
files:       circuits/web/servers.py
description:
fixed a set/tuple init


changeset:   2458:820e92ca65ee
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 00:43:14 2011 +0200
files:       circuits/core/components.py
description:
don't pass extra arguments to object.__init__


changeset:   2459:65a14a8d5b5f
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 00:44:59 2011 +0200
files:       circuits/tools/__init__.py circuits/web/dispatchers/jsonrpc.py
description:
fixed tryimport to accept a string as argument in addition to tuples


changeset:   2460:d64ce8c15bf0
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 00:45:55 2011 +0200
files:       circuits/web/controllers.py
description:
fixed metaclasses trick for web/servers.py


changeset:   2461:75cd94c6dc40
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 01:17:54 2011 +0200
files:       circuits/web/controllers.py
description:
fixed metaclasses trick for web/servers.py (again)


changeset:   2462:a1ed88946a80
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 01:59:56 2011 +0200
files:       circuits/web/_httpauth.py tests/web/test_basicauth.py
description:
fixes for basicauth for py26


changeset:   2463:c951fc73d395
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 03:04:32 2011 +0200
files:       circuits/web/wrappers.py tests/conftest.py tests/web/test_basicauth.py tests/web/test_cookies.py tests/web/test_core.py
description:
more tests fixing


changeset:   2464:c3602a626325
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 19:19:53 2011 +0200
files:       circuits/net/sockets.py circuits/tools/__init__.py tests/net/test_tcp.py tests/web/test_expires.py tests/web/test_json.py tests/web/test_logger.py tests/web/websocket.py
description:
more tests pass


changeset:   2465:cab632d743dd
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 19:50:05 2011 +0200
files:       circuits/web/wrappers.py
description:
only encode cookies if they don't match str type


changeset:   2466:2b1b8d31712d
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 23 19:50:48 2011 +0200
files:       circuits/web/http.py
description:
data is bytes buffer so use b'\r\n\r\n' instead


changeset:   2467:c3914b6f8348
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 00:58:37 2011 +0200
files:       circuits/core/debugger.py circuits/web/http.py tests/core/test_utils.py tests/web/test_core.py tests/web/test_http.py tests/web/test_websockets.py tests/web/websocket.py
description:
more tests fixes


changeset:   2468:fb3e6a4f3765
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 01:05:23 2011 +0200
files:       circuits/tools/__init__.py circuits/web/utils.py
description:
removed unused imports


changeset:   2469:b954aa0b05e4
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 01:18:38 2011 +0200
files:       tests/web/test_utils.py
description:
fixes for utils.decompress in py2


changeset:   2470:489c2ca3d643
user:        prologic
date:        Sun Apr 24 12:20:15 2011 +1000
files:       tests/app/test_daemon.py tests/app/test_logger.py tests/core/test_bridge.py tests/core/test_ipc.py tests/web/test_gzip.py tests/web/test_jsonrpc.py tests/web/test_multipartformdata.py tests/web/test_web_task.py tests/web/test_wsgi_application.py tests/web/test_wsgi_application_generator.py tests/web/test_wsgi_application_yield.py
description:
Removed all pytest.skip(...)


changeset:   2471:924c3c008b35
user:        prologic
date:        Sun Apr 24 12:37:31 2011 +1000
files:       tmp/cython/hello.c tmp/cython/hello.pyx tmp/cython/setup.py
description:
Added simple Hello World Cython extension module


changeset:   2472:cf616d039b33
parent:      2469:b954aa0b05e4
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 03:16:04 2011 +0200
files:       tests/web/test_websockets.py
description:
change skipif to skip for websockets tests


changeset:   2473:b241eeea484a
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 04:14:45 2011 +0200
files:       tests/web/helpers.py tests/web/jsonrpclib.py tests/web/test_basicauth.py tests/web/test_cookies.py tests/web/test_core.py tests/web/test_digestauth.py tests/web/test_exceptions.py tests/web/test_expires.py tests/web/test_expose.py tests/web/test_future.py tests/web/test_generator.py tests/web/test_gzip.py tests/web/test_json.py tests/web/test_jsonrpc.py tests/web/test_logger.py tests/web/test_multipartformdata.py tests/web/test_null_response.py tests/web/test_request_failure.py tests/web/test_serve_download.py tests/web/test_serve_file.py tests/web/test_servers.py tests/web/test_sessions.py tests/web/test_static.py tests/web/test_unicode.py tests/web/test_value.py tests/web/test_web_task.py tests/web/test_wsgi_application.py tests/web/test_wsgi_application_generator.py tests/web/test_wsgi_application_yield.py tests/web/test_wsgi_gateway.py tests/web/test_wsgi_gateway_errors.py tests/web/test_wsgi_gateway_generator.py tests/web/test_wsgi_gateway_yield.py tests/web/test_xmlrpc.py tests/web/test_yield.py tests/web/websocket.py
description:
factored tests/web imports try...catch for py2/3 in tests/web/helpers.py


changeset:   2474:31b9340ac62c
parent:      2473:b241eeea484a
parent:      2471:924c3c008b35
user:        prologic
date:        Sun Apr 24 12:41:54 2011 +1000
files:       tests/web/test_gzip.py tests/web/test_jsonrpc.py tests/web/test_multipartformdata.py tests/web/test_web_task.py tests/web/test_wsgi_application.py tests/web/test_wsgi_application_generator.py tests/web/test_wsgi_application_yield.py
description:
Merged with 924c3c008b35


changeset:   2475:b8c14e5aafeb
parent:      2473:b241eeea484a
parent:      2470:489c2ca3d643
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 04:38:23 2011 +0200
files:       tests/web/test_gzip.py tests/web/test_jsonrpc.py tests/web/test_multipartformdata.py tests/web/test_web_task.py tests/web/test_wsgi_application.py tests/web/test_wsgi_application_generator.py tests/web/test_wsgi_application_yield.py
description:
merged with main branch


changeset:   2476:64aa0492904c
parent:      2475:b8c14e5aafeb
parent:      2474:31b9340ac62c
user:        prologic
date:        Sun Apr 24 12:47:09 2011 +1000
files:       tests/web/test_jsonrpc.py tests/web/test_wsgi_application.py tests/web/test_wsgi_application_generator.py tests/web/test_wsgi_application_yield.py
description:
Merged with 31b9340ac62c


changeset:   2477:a628a2e09dab
parent:      2475:b8c14e5aafeb
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 05:00:42 2011 +0200
files:       circuits/core/manager.py tests/web/test_web_task.py
description:
s/process.isAlive/process.is_alive


changeset:   2478:4abc28aa76db
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 14:35:14 2011 +0200
files:       circuits/net/sockets.py
description:
fixes a race condition bug with UNIXClient that would prevent it from adding read listener on startup


changeset:   2479:c9fd4a763135
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 14:35:42 2011 +0200
files:       tests/web/test_web_task.py
description:
removed debugged output for web task test


changeset:   2480:3d4bc23fff34
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 14:36:05 2011 +0200
files:       circuits/web/http.py
description:
removed debugging output in web/http.py


changeset:   2481:7eb3185734df
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 14:37:49 2011 +0200
files:       circuits/core/debugger.py
description:
fixes some comments typos


changeset:   2482:f6cf1e74cba3
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 14:38:11 2011 +0200
files:       circuits/core/bridge.py
description:
fixes for py2 imports


changeset:   2483:3a0b04d74a2f
user:        Osso <adeiana@gmail.com>
date:        Sun Apr 24 15:20:18 2011 +0200
files:       circuits/net/sockets.py
description:
in client only encode data if not of type bytes


changeset:   2484:e9bef31f8768
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 04:40:18 2011 +0200
files:       circuits/core/bridge.py tests/web/test_web_task.py
description:
fixes for test_web_task.py, bridge was trying to unpickle bytes with StringIO


changeset:   2485:d4dd36180e43
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 05:30:02 2011 +0200
files:       tests/app/test_daemon.py
description:
fixes for app/test_daemon.py, was assuming python executable was called python


changeset:   2486:caf821d3d124
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 05:54:36 2011 +0200
files:       circuits/app/log.py tests/app/test_logger.py
description:
test logger.exception in an exception to make it work


changeset:   2487:f950837c34bd
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 06:34:56 2011 +0200
files:       tests/core/test_signals.py
description:
removed cov requirement from core/test_signals.py


changeset:   2488:1c0dffcc4f14
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 06:35:45 2011 +0200
files:       circuits/app/daemon.py
description:
fixes for daemonizer, was failing to exit parents


changeset:   2489:8b997290642b
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:26:46 2011 +0200
files:       tests/web/test_gzip.py
description:
handle imports for py2/3 in web/test_gzip.py


changeset:   2490:1309ddbfb0eb
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:27:16 2011 +0200
files:       tests/app/test_logger.py
description:
removed debug print in app/test_logger.py


changeset:   2491:7a989451e42c
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:28:03 2011 +0200
files:       circuits/web/utils.py
description:
test for isinstance(bytes) instead of isinstance(str) before encoding


changeset:   2492:46038670d7d9
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:29:07 2011 +0200
files:       circuits/web/http.py
description:
handle response data in bytes, to be compatible with gzipped responses


changeset:   2493:519ff77aa76d
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:29:44 2011 +0200
files:       circuits/net/sockets.py
description:
test for isinstance(bytes) instead of isinstance(str) before encoding


changeset:   2494:89c396bba664
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:31:08 2011 +0200
files:       circuits/app/log.py
description:
removed debug print in app/log.py


changeset:   2495:f0a5f196c2af
user:        Osso <adeiana@gmail.com>
date:        Mon Apr 25 07:32:25 2011 +0200
files:       circuits/core/debugger.py
description:
make sure we are not writing bytes in Debugger StringIO


changeset:   2496:b510ab3d605e
parent:      2495:f0a5f196c2af
parent:      2476:64aa0492904c
user:        prologic
date:        Mon Apr 25 20:17:28 2011 +1000
description:
Merged with 64aa0492904c


changeset:   2497:3de98759786f
user:        prologic
date:        Tue Apr 26 10:45:59 2011 +1000
files:       .hgchurn
description:
Added churn alias file


changeset:   2498:08e6bfcb9fe2
user:        prologic
date:        Wed Apr 27 06:08:50 2011 +1000
files:       circuits/net/sockets.py
description:
- Fixed a missing Event ``Closed()`` not being triggered for ``UDPServer``.


changeset:   2499:4bc48750314d
user:        Alex Mayfield <alexmax2742@gmail.com>
date:        Tue Apr 26 22:54:33 2011 -0400
files:       circuits/net/sockets.py
description:
Yank encoding out of socket layer.


changeset:   2500:f9e16d7efccd
user:        Alex Mayfield <alexmax2742@gmail.com>
date:        Tue Apr 26 23:08:27 2011 -0400
files:       circuits/web/servers.py
description:
Stop trying to create HTTP server with removed socket-level encoding.


changeset:   2501:9c2ad2a3096d
user:        jamesmills
date:        Wed Apr 27 05:55:24 2011 +0000
files:       circuits/net/sockets.py
description:
Make underlyingh ``UDPServer`` socket reuseable by setting ``SO_REUSEADDR``


changeset:   2502:3f465571a3ef
user:        jamesmills
date:        Wed Apr 27 05:55:54 2011 +0000
files:       circuits/web/wsgi.py
description:
Fixed incorrect channel name/target for ``Application`` Web Component


changeset:   2503:5a5f9cbb3cfb
user:        jamesmills
date:        Wed Apr 27 06:17:11 2011 +0000
files:       tests/core/test_pools.py
description:
Compute values before asserting


changeset:   2504:934dfbc768dc
user:        jamesmills
date:        Wed Apr 27 06:17:47 2011 +0000
files:       tests/web/jsonrpclib.py
description:
Fixed invalid py2/py3 imports for urllib/httplib stuff.


changeset:   2505:cab0b3d99228
user:        jamesmills
date:        Wed Apr 27 06:23:22 2011 +0000
files:       tests/core/test_pools.py
description:
Maybe a sleep(1) makes this test pass more reliably?


changeset:   2506:50274cbb4692
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 16:59:40 2011 +0200
files:       circuits/web/http.py
description:
always decode http headers and url with utf-8


changeset:   2507:931cbf9d145b
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 17:01:53 2011 +0200
files:       circuits/web/http.py
description:
always send binary data to socket


changeset:   2508:196d0b822001
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 17:28:48 2011 +0200
files:       circuits/web/http.py circuits/web/wrappers.py
description:
encode the body of http requests on value_changed in the body where we know the encoding to use instead of always encoding to utf-8 in the response object


changeset:   2509:0a3305c4039c
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 18:15:26 2011 +0200
files:       circuits/web/http.py
description:
always encode headers in response using utf-8


changeset:   2510:a6804cbac512
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 18:18:58 2011 +0200
files:       circuits/web/wrappers.py
description:
add an encoding parameter to http responses


changeset:   2511:3a8226c00ffb
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 18:19:44 2011 +0200
files:       circuits/web/servers.py
description:
pass parameter from Server to HTTP instance


changeset:   2512:aa94c0640391
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 18:28:40 2011 +0200
files:       circuits/web/http.py circuits/web/wrappers.py
description:
response now has an encoding parameter, so we don't need to encode the body before sending it to the response anymore


changeset:   2513:cc03f44c97fe
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 19:19:03 2011 +0200
files:       circuits/net/sockets.py tests/net/server.py tests/net/test_tcp.py
description:
fixes server socket being discarded twice on close + disconnect


changeset:   2514:a5eadca6708d
user:        Alessio Deiana <adeiana@gmail.com>
date:        Wed Apr 27 19:49:30 2011 +0200
files:       tests/web/test_wsgi_application.py
description:
fixes for test_wsgi_application sending unicode for python2 and not encoding post data for python3


changeset:   2515:38b9459c8cf4
user:        jamesmills
date:        Wed Apr 27 23:18:52 2011 +0000
files:       tests/web/test_websockets.py
description:
Renable websockets test - it isn't looping but failing because of unicode issues


changeset:   2516:0e203d3990f0
user:        jamesmills
date:        Wed Apr 27 23:19:06 2011 +0000
files:       circuits/web/http.py
description:
Use self._encoding


changeset:   2517:a5d871f148f0
user:        jamesmills
date:        Thu Apr 28 01:27:02 2011 +0000
files:       docs/source/index.rst docs/source/roadmap.rst
description:
Added a RoadMap in docs...


changeset:   2518:8ba4d9ef398c
user:        jamesmills
date:        Thu Apr 28 01:32:21 2011 +0000
files:       docs/source/roadmap.rst
description:
Updated RoadMap for 1.6


changeset:   2519:465141673a7a
user:        jamesmills
date:        Thu Apr 28 01:48:00 2011 +0000
files:       circuits/core/futures.py
description:
Added doc string for @future


changeset:   2520:ec457d063a0d
user:        jamesmills
date:        Thu Apr 28 01:51:16 2011 +0000
files:       circuits/core/workers.py
description:
Added doc string for Worker


changeset:   2521:ef167dd35e8a
parent:      2514:a5eadca6708d
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:24:47 2011 +0200
files:       tests/web/test_multipartformdata.py
description:
fixes for py2/3 import


changeset:   2522:400971939b6a
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:24:58 2011 +0200
files:       tests/net/test_udp.py
description:
fixes udp test, send binary data to socket


changeset:   2523:3fa5c42b631c
parent:      2521:ef167dd35e8a
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:25:45 2011 +0200
files:       tests/net/test_udp.py
description:
fixes udp test, send binary data to socket


changeset:   2524:7904f13f0c1c
parent:      2522:400971939b6a
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:28:09 2011 +0200
files:       tests/web/test_encodings.py
description:
added tests for http using an encoding that is not utf-8


changeset:   2525:265e46dde8b0
parent:      2524:7904f13f0c1c
parent:      2523:3fa5c42b631c
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:29:28 2011 +0200
files:       tests/net/test_udp.py
description:
merged branch made by mistake


changeset:   2526:9eb847945241
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:29:56 2011 +0200
files:       tests/net/test_udp.py
description:
removed debugger from test_udp


changeset:   2527:bcc3c09a16da
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:32:11 2011 +0200
files:       tests/net/test_udp.py
description:
fixes removed debugger from test_udp (removed manager creation line)


changeset:   2528:9055c84e20bd
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:34:00 2011 +0200
files:       tests/net/test_pipe.py
description:
send binary data to socket in test_pipe


changeset:   2529:19f8d1743ed8
user:        Osso <adeiana@gmail.com>
date:        Wed Apr 27 23:35:16 2011 +0200
files:       tests/net/test_unix.py
description:
send binary data to socket in test_unix


changeset:   2530:193dbe61a76a
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 01:44:05 2011 +0200
files:       tests/web/test_client.py
description:
use wait for event in web/test_client


changeset:   2531:11b0490740fd
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 01:44:25 2011 +0200
files:       tests/web/test_encodings.py
description:
fixes test for py3


changeset:   2532:e5118b71873c
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 01:45:18 2011 +0200
files:       circuits/web/http.py
description:
fixes encoding not being passed to Reponse object, but seems to break the generator


changeset:   2533:efbeff3d4c48
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 01:53:54 2011 +0200
files:       circuits/web/http.py
description:
fixes web/test_generator


changeset:   2534:a8c56768c134
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 02:35:15 2011 +0200
files:       tests/web/jsonrpclib.py
description:
fixes for py3 and jsonrpclib


changeset:   2535:84303842e135
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 02:35:59 2011 +0200
files:       tests/web/test_jsonrpc.py
description:
pass encoding to jsonrpclib in web/test_jsonrpc


changeset:   2536:c1be5fb76cf5
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 03:00:54 2011 +0200
files:       circuits/web/dispatchers/jsonrpc.py tests/core/signalapp.py tests/web/jsonrpclib.py
description:
fixes web/test_jsonrpc


changeset:   2537:618a665ac94b
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 03:05:43 2011 +0200
files:       tests/web/test_http.py
description:
write bytes to socket in test_http


changeset:   2538:4bc62f701554
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 03:06:14 2011 +0200
files:       tests/web/test_http.py
description:
removed debugger from test_http


changeset:   2539:411ceb2bf4a6
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 03:26:54 2011 +0200
files:       tests/web/multipartform.py tests/web/test_multipartformdata.py
description:
fixes for web/test_multipartformdata.py


changeset:   2540:b2d1e8ee62ff
parent:      2539:411ceb2bf4a6
parent:      2520:ec457d063a0d
user:        Osso <adeiana@gmail.com>
date:        Thu Apr 28 21:18:22 2011 +0200
files:       circuits/web/http.py
description:
merged main branch ec457d063a0d


changeset:   2541:15f4f7aee997
user:        Osso <adeiana@gmail.com>
date:        Fri Apr 29 01:06:44 2011 +0200
files:       circuits/core/debugger.py circuits/web/dispatchers/websockets.py circuits/web/wrappers.py tests/web/test_websockets.py tests/web/websocket.py
description:
fixes for websockets, websockets tests and debugger encoding handling


changeset:   2542:67d91ef4d997
user:        Osso <adeiana@gmail.com>
date:        Fri Apr 29 01:50:03 2011 +0200
files:       circuits/web/wrappers.py
description:
fix for generators and body, content length was consuming the generator


changeset:   2543:44e74da93c96
user:        Osso <adeiana@gmail.com>
date:        Fri Apr 29 02:03:23 2011 +0200
files:       tests/core/signalapp.py tests/core/test_signals.py
description:
sleep to pass test_signal more reliably


changeset:   2544:9c14a3a00d5c
user:        Osso <adeiana@gmail.com>
date:        Fri Apr 29 02:49:28 2011 +0200
files:       circuits/web/client.py tests/conftest.py tests/web/test_client.py
description:
fixes for http client and http client test


changeset:   2545:34249afdb65c
user:        jamesmills
date:        Fri Apr 29 01:23:31 2011 +0000
files:       tests/web/test_multipartformdata.py
description:
Fixed tests.web.test_multipartformdata by using BytesIO(...) -- NB: circuits (tip) is no longer compatible with Python 2.5


changeset:   2546:dbf2a113f8df
user:        jamesmills
date:        Fri Apr 29 01:50:26 2011 +0000
files:       tests/web/test_multipartformdata.py
description:
Fixed (again) tests.web.test_multipartformdata for _both_ Python 2 and 3 (tested with 2.7 and 3.2)


changeset:   2547:793434309f47
user:        prologic
date:        Fri Apr 29 20:36:34 2011 +1000
files:       circuits/web/__main__.py circuits/web/main.py scripts/circuits.web tests/web/test_main.py
description:
Added system test for circuits.web (the script)


changeset:   2548:bb86980938e0
user:        prologic
date:        Fri Apr 29 21:02:39 2011 +1000
files:       tests/web/test_main.py
description:
Fixed checking of err.ERRCONNREFUSED and removed erroneous pdb


changeset:   2549:d31d1e3d7d09
user:        prologic
date:        Fri Apr 29 21:02:58 2011 +1000
files:       tests/net/client.py tests/net/test_udp.py
description:
Added assertion testing CLose() event on a UDPServer/UDPClient


changeset:   2550:e9be6f99b337
user:        prologic
date:        Fri Apr 29 22:01:34 2011 +1000
files:       circuits/net/sockets.py tests/net/server.py tests/net/test_tcp.py
description:
Fixed a bug with binding to an int (port) in the Client Socket Component


changeset:   2551:46f42d45e89f
user:        prologic
date:        Fri Apr 29 22:01:58 2011 +1000
files:       tests/net/test_client.py
description:
Added tests that test the binding behavior (int/str) of Client Socket Components


changeset:   2552:442210ebca65
user:        prologic
date:        Fri Apr 29 22:13:20 2011 +1000
files:       circuits/drivers/__init__.py circuits/drivers/_gtk.py circuits/drivers/_inotify.py circuits/drivers/_pygame.py circuits/io/notify.py
description:
Removed circuits.drivers and added circuits.io.notify. Why ? Testing drivers for gtk/pygame is really hard. If anyone really wants this feel free to implement it yourself (it's not hard)


changeset:   2553:76ae9b50ddc4
user:        prologic
date:        Fri Apr 29 22:28:01 2011 +1000
files:       circuits/core/manager.py
description:
Added deprecation warnings for .push .add and .remove methods


changeset:   2554:4f5fb32505ba
user:        prologic
date:        Fri Apr 29 22:43:51 2011 +1000
files:       docs/source/api/circuits_app_config.rst docs/source/api/circuits_app_env.rst docs/source/api/circuits_core_handlers.rst docs/source/api/circuits_drivers.rst docs/source/api/circuits_drivers_gtk.rst docs/source/api/circuits_drivers_inotify.rst docs/source/api/circuits_drivers_pygame.rst docs/source/api/circuits_io_notify.rst docs/source/api/circuits_web_headers.rst docs/source/api/circuits_web_main.rst docs/source/api/circuits_web_utils.rst
description:
Updated docs


changeset:   2555:658bd076e5d0
user:        prologic
date:        Fri Apr 29 23:19:53 2011 +1000
files:       circuits/core/pollers.py tests/net/test_pipe.py tests/net/test_tcp.py tests/net/test_udp.py tests/net/test_unix.py
description:
Tided up circuits.core.pollers a bit by removing teh imports and using attribute access in place of


changeset:   2556:bc3b32751ab4
user:        prologic
date:        Sat Apr 30 10:13:22 2011 +1000
files:       RELEASE.rst
description:
Starting to prepare release notes for 1.6


changeset:   2557:b59960e031b3
bookmark:    auto_init
parent:      2375:42e311b4d809
user:        jamesmills
date:        Wed Mar 16 00:52:52 2011 +0000
files:       circuits/core/components.py circuits/core/manager.py
description:
- Experimental Auto Component Initialization

Automatically initializes components by ensuring Manager, BaseComponent
and Component constructors are called automatically without having to
worry about calling ``super(MyComponent, self).__init__(...)``


changeset:   2558:9c187730386d
parent:      2375:42e311b4d809
user:        jamesmills
date:        Wed Mar 16 00:58:35 2011 +0000
files:       circuits/core/manager.py circuits/core/values.py
description:
- Experimental Result Proxy support for result/value management

This adds support for returning Result objects (*as opposed to Value
objects*) which hold a ``Value`` object which in turn encapsulates
the return value from an event handler by proxying it and all
method and special method calls on it. This allows you to write code
like this::

   class App(Component):

   def test(self):
      x = self.push(Foo())
      y = self.push(Bar())
      return x.value + y.value


changeset:   2559:4b382885aae7
parent:      2555:658bd076e5d0
user:        prologic
date:        Sat Apr 30 10:05:33 2011 +1000
files:       circuits/core/manager.py test_event_lock.py
description:
Experimental Event Lock Detection


changeset:   2560:68130a057e1a
user:        prologic
date:        Sat Apr 30 12:35:09 2011 +1000
files:       circuits/core/manager.py test_event_lock.py
description:
Backed out changeset 4b382885aae7 - Broken experiment with event lock
detection.


changeset:   2561:62c8d767f28b
parent:      2560:68130a057e1a
parent:      2556:bc3b32751ab4
user:        prologic
date:        Sat Apr 30 12:36:06 2011 +1000
description:
Merged with bc3b32751ab4


changeset:   2562:b6e276ce1796
parent:      2561:62c8d767f28b
parent:      2558:9c187730386d
user:        prologic
date:        Sat Apr 30 12:36:52 2011 +1000
files:       circuits/core/manager.py circuits/core/values.py
description:
Merged with and discarded result_proxy head/bookmark (broken)


changeset:   2563:b199e6eb4fd8
parent:      2562:b6e276ce1796
parent:      2557:b59960e031b3
user:        prologic
date:        Sat Apr 30 12:37:14 2011 +1000
files:       circuits/core/components.py circuits/core/manager.py
description:
Merged with and discarded auto_init head/bookmark (broken)


changeset:   2564:b894946e8fe9
user:        prologic
date:        Sat Apr 30 13:11:05 2011 +1000
files:       .hgchurn
description:
Updated churn alias file


changeset:   2565:2f2f0eac94a0
user:        prologic
date:        Sun May 01 23:14:27 2011 +1000
files:       circuits/web/controllers.py
description:
Updated docs


changeset:   2566:a2b82e1a236b
parent:      2563:b199e6eb4fd8
user:        prologic
date:        Sat Apr 30 12:51:30 2011 +1000
files:       circuits/core/manager.py test_greenlets.py
description:
Make each event handler executed inside a greenlet


changeset:   2567:defaa85af5d1
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:18:44 2011 +0200
files:       circuits/core/manager.py
description:
working proof for manager.wait_event


changeset:   2568:d0101454f7de
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:20:37 2011 +0200
files:       circuits/core/manager.py
description:
delete event from wait_handlers after we have reached it


changeset:   2569:eae9c53cb206
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:27:22 2011 +0200
files:       circuits/core/manager.py
description:
handle lists of events in wait_event


changeset:   2570:20f05f7e84bc
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:27:35 2011 +0200
files:       test.py
description:
added example test for greenlets


changeset:   2571:d9ef4955baa7
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:39:37 2011 +0200
files:       circuits/core/manager.py test.py
description:
added a simple call for synchronous calls to events


changeset:   2572:f34ed5025350
parent:      2570:20f05f7e84bc
user:        prologic
date:        Sat Apr 30 13:40:11 2011 +1000
files:       test.py
description:
Now let's make it work like this (See test.py)


changeset:   2573:00de9286ac73
parent:      2572:f34ed5025350
parent:      2571:d9ef4955baa7
user:        prologic
date:        Sat Apr 30 13:41:03 2011 +1000
files:       test.py
description:
Merged with f34ed5025350


changeset:   2574:04966187e0de
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 05:43:04 2011 +0200
files:       test.py
description:
use call() instead of fire()


changeset:   2575:f2eea27ed87f
user:        prologic
date:        Sat Apr 30 13:58:50 2011 +1000
files:       test_greenlets.py
description:
Removed broken test case


changeset:   2576:8d443de69ac9
user:        prologic
date:        Sat Apr 30 14:02:40 2011 +1000
files:       test.py tests/core/test_greenlet.py
description:
Make this into a proper unit test


changeset:   2577:70444edc85a2
user:        prologic
date:        Sat Apr 30 14:11:53 2011 +1000
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
Modifying test case for .waitEvent(...)


changeset:   2578:5c4a6361ef4e
user:        prologic
date:        Sat Apr 30 14:19:45 2011 +1000
files:       tests/core/test_greenlet.py
description:
This should work :/


changeset:   2579:51b56773e71a
user:        prologic
date:        Sat Apr 30 14:48:13 2011 +1000
files:       tests/core/test_greenlet.py
description:
Fixed test for .waitEvent(...)


changeset:   2580:b335e417684d
user:        prologic
date:        Sat Apr 30 15:17:11 2011 +1000
files:       tests/core/test_greenlet.py
description:
Updated test to tesT_wait_class


changeset:   2581:c3041205fd20
user:        prologic
date:        Sat Apr 30 15:18:22 2011 +1000
files:       tests/core/test_greenlet.py
description:
Added test_wait_instance (which fails and isn't implemetned yet)


changeset:   2582:570d6e1ec73a
user:        prologic
date:        Sat Apr 30 15:19:30 2011 +1000
files:       circuits/core/manager.py
description:
Changed attribute name we store active handlers in to _active_handlers


changeset:   2583:ad63c7eeede9
user:        prologic
date:        Sat Apr 30 15:22:55 2011 +1000
files:       circuits/core/manager.py
description:
Renamed some variables to make things a bit more clear :)


changeset:   2584:3a8073ecfaa4
user:        prologic
date:        Sat Apr 30 15:24:48 2011 +1000
files:       circuits/core/manager.py
description:
Fixed event filters


changeset:   2585:565c1e14adaa
user:        prologic
date:        Sat Apr 30 15:53:58 2011 +1000
files:       tests/web/test_main.py
description:
raise an AssertionError if any other error


changeset:   2586:837c9a9762bd
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 08:12:26 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
all greenlet manager handling, no threads


changeset:   2587:a1b99a264249
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 08:17:29 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
added a ticks limit for waitEvent


changeset:   2588:8b8aea2c4d6c
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 08:20:44 2011 +0200
files:       tests/core/test_greenlet.py
description:
fixed greenlet test


changeset:   2589:07d6b9bf415a
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 08:22:48 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
fixed greenlet test


changeset:   2590:31316f690a6d
user:        prologic
date:        Sat Apr 30 16:43:05 2011 +1000
files:       circuits/core/manager.py
description:
Added an alias for start -> run


changeset:   2591:b86f410e8fb1
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 09:46:37 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
new test_wait_component


changeset:   2592:62fbda05d9ef
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 22:43:47 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
new implementation of waitEvent using only .switch and not array for events


changeset:   2593:6a17762ca2cd
parent:      2585:565c1e14adaa
user:        prologic
date:        Sat Apr 30 18:10:07 2011 +1000
files:       circuits/core/manager.py
description:
Added support for matching event instances for .waitEvent(...)


changeset:   2594:0c1016fab127
parent:      2593:6a17762ca2cd
parent:      2591:b86f410e8fb1
user:        prologic
date:        Sat Apr 30 18:24:23 2011 +1000
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
Merged with b86f410e8fb1 (broken)


changeset:   2595:288d8e00a253
parent:      2592:62fbda05d9ef
parent:      2594:0c1016fab127
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 23:12:55 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
merged with 0c1016fab127


changeset:   2596:4f3517882a96
user:        Osso <adeiana@gmail.com>
date:        Sat Apr 30 23:44:20 2011 +0200
files:       tests/core/test_greenlet.py
description:
simplified test_greenlet


changeset:   2597:b59c2e038aa6
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 01:53:29 2011 +0200
files:       circuits/core/manager.py
description:
go back to caller in waitEvent instead of always maingreenlet


changeset:   2598:c7b4b5105020
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 01:58:27 2011 +0200
files:       circuits/core/manager.py
description:
renamed _process to _proc cause of conflicting _process func


changeset:   2599:d0ba8ce0156a
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 01:59:15 2011 +0200
files:       circuits/core/manager.py
description:
renamed _process to _proc cause of conflicting _process func


changeset:   2600:f5ac20a466a6
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 02:58:09 2011 +0200
files:       circuits/core/manager.py
description:
fixes for changed run params


changeset:   2601:ae133d505134
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 03:00:28 2011 +0200
files:       tests/web/test_web_task.py
description:
fixes for tests/web/test_web_task


changeset:   2602:bda273bae78e
parent:      2601:ae133d505134
parent:      2564:b894946e8fe9
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 04:46:54 2011 +0200
description:
merge with b894946e8fe9


changeset:   2603:8628e31badd9
user:        Osso <adeiana@gmail.com>
date:        Sun May 01 05:05:33 2011 +0200
files:       circuits/core/manager.py
description:
remove unused Manager._active_handlers


changeset:   2604:87b937e200cc
parent:      2603:8628e31badd9
parent:      2565:2f2f0eac94a0
user:        prologic
date:        Sun May 01 23:14:40 2011 +1000
description:
Automated merge with https://bitbucket.org/osso/circuits/


changeset:   2605:d7d7b438eeb5
user:        prologic
date:        Sun May 01 23:23:30 2011 +1000
files:       circuits/web/controllers.py
description:
Fixed a bug I introduced in 2f2f0eac94a0 by trying to reindent this module and tidy it up :/


changeset:   2606:0a5dff89163d
user:        prologic
date:        Mon May 02 00:10:03 2011 +1000
files:       circuits/core/manager.py circuits/web/main.py tests/core/test_signals.py
description:
Tided up manager module. Removed Python 2.5 support. Removed SIGHUP signal
handler.


changeset:   2607:2f560d71126f
user:        jamesmills
date:        Tue May 03 02:35:26 2011 +0000
files:       tests/core/test_pools.py
description:
Tided up tests.core.test_pools


changeset:   2608:f56e0d33fb31
user:        jamesmills
date:        Fri May 06 01:08:49 2011 +0000
files:       README.rst circuits/app/daemon.py circuits/core/components.py circuits/core/events.py circuits/core/values.py circuits/core/workers.py circuits/net/protocols/irc.py circuits/net/sockets.py docs/source/guides/server.rst docs/source/tutorial/index.rst examples/web/forms.py examples/web/tpl/index.html
description:
Updated docs - Fixed all incorrect uses of it's vs its


changeset:   2609:1aa734aa9e8f
user:        prologic
date:        Fri May 06 11:13:09 2011 +1000
files:       docs/source/api/circuits.rst
description:
Updated docs - Removed reference to non-existent AOU document circuits_drivers


changeset:   2610:22a89b600207
user:        prologic
date:        Sun May 08 08:50:13 2011 +1000
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
Make greenlet features optional


changeset:   2611:41673f96c47e
user:        prologic
date:        Sun May 08 08:53:56 2011 +1000
files:       circuits/core/manager.py
description:
Fixed _flush for making greenlet features optional


changeset:   2612:c36b756c4ffb
user:        prologic
date:        Wed May 11 10:49:27 2011 +1000
files:       examples/pygameex.py
description:
Removed obsoluete example (circuits can still be used with pygame though... if anyone needs this it can be easily re-implemetned as a recipe)


changeset:   2613:6b9aa1a2d753
user:        prologic
date:        Wed May 11 10:50:01 2011 +1000
files:       docs/source/_themes/om/genindex.html docs/source/_themes/om/layout.html docs/source/_themes/om/modindex.html docs/source/_themes/om/search.html docs/source/_themes/om/static/default.css docs/source/_themes/om/static/djangodocs.css docs/source/_themes/om/static/docicons-behindscenes.png docs/source/_themes/om/static/docicons-note.png docs/source/_themes/om/static/docicons-philosophy.png docs/source/_themes/om/static/homepage.css docs/source/_themes/om/static/reset-fonts-grids.css docs/source/_themes/om/theme.conf docs/source/conf.py
description:
Updated docs with a borrowed theme from django


changeset:   2614:8907d5dadf87
user:        prologic
date:        Wed May 11 10:51:36 2011 +1000
files:       tests/net/test_udp.py
description:
Added a new test (thanks to AlexMax) which tests for closing a listening socket on a given port and reopening it again -- which fails currently


changeset:   2615:31d4a702493e
parent:      2611:41673f96c47e
user:        prologic
date:        Wed May 11 10:02:02 2011 +1000
files:       circuits/net/sockets.py docs/source/conf.py examples/pygameex.py tests/net/test_udp.py
description:
Removed obsoluete example (circuits can still be used with pygame though... if anyone needs this it can be easily re-implemetned as a recipe)


changeset:   2616:53e2e8d03b97
parent:      2615:31d4a702493e
parent:      2614:8907d5dadf87
user:        prologic
date:        Wed May 11 10:52:24 2011 +1000
files:       tests/net/test_udp.py
description:
Merged with 8907d5dadf87


changeset:   2617:50ee7a8857cc
parent:      2603:8628e31badd9
user:        Alessio Deiana <adeiana@gmail.com>
date:        Mon May 02 15:04:03 2011 +0200
files:       circuits/core/manager.py tests/core/test_greenlet.py
description:
removed extra .value from callEvent when return event value, added test for callEvent


changeset:   2618:55c3b206bc84
user:        Alessio Deiana <adeiana@gmail.com>
date:        Mon May 02 15:14:22 2011 +0200
files:       tests/core/test_greenlet.py
description:
added test_greenlet for callEvent returning a null value


changeset:   2619:0e507fa9e035
parent:      2618:55c3b206bc84
parent:      2616:53e2e8d03b97
user:        prologic
date:        Thu May 12 07:36:29 2011 +1000
files:       circuits/core/manager.py examples/pygameex.py tests/core/test_greenlet.py
description:
Automated merge with https://bitbucket.org/osso/circuits/


changeset:   2620:37557766d63f
parent:      2616:53e2e8d03b97
user:        aspidites
date:        Wed May 11 10:49:24 2011 -0500
files:       examples/cat.py examples/echoserver.py examples/ircbot.py examples/ircclient.py examples/portforward.py examples/telnet.py examples/udplatency.py
description:
Patch by Aspidites:
	- updated push calls to fire


changeset:   2621:fd919c2b7a96
parent:      2620:37557766d63f
parent:      2619:0e507fa9e035
user:        prologic
date:        Thu May 12 07:36:37 2011 +1000
description:
Automated merge with https://bitbucket.org/aspidites/circuits/


changeset:   2622:03acd2800a37
user:        prologic
date:        Fri May 13 09:07:12 2011 +1000
files:       .hgchurn docs/source/contributors.rst docs/source/index.rst
description:
Updated churn alias files and added documentation for circuits contributors


changeset:   2623:b94908326c87
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 15:13:57 2011 +0200
files:       tests/net/test_udp.py
description:
bind to a free port instead of fixed port


changeset:   2624:ec7864defd6c
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 15:37:05 2011 +0200
files:       circuits/net/sockets.py
description:
handle closing of udpserver socket when no client is connected


changeset:   2625:517bf5f6479a
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 16:22:21 2011 +0200
files:       circuits/core/components.py
description:
use removeHandler instead of remove


changeset:   2626:187a324fabfc
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 17:59:29 2011 +0200
files:       circuits/core/components.py
description:
unregister event for components


changeset:   2627:293179da866d
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:01:02 2011 +0200
files:       circuits/core/events.py
description:
unregister event class


changeset:   2628:b24c5e3525d8
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:01:52 2011 +0200
files:       tests/core/test_component_repr.py
description:
updated test_component_repr to consider unregister event when counting for binded handlers


changeset:   2629:1f01763756eb
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:02:48 2011 +0200
files:       tests/net/server.py tests/net/test_udp.py
description:
use .fire() instead of .push()


changeset:   2630:e132be3aa171
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:04:26 2011 +0200
files:       circuits/tools/__init__.py
description:
make util.kill() use events for unregistering components


changeset:   2631:d55336967e32
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:25:46 2011 +0200
files:       tests/net/test_udp.py
description:
unregister components using an event, kill won't work from a different thread


changeset:   2632:af196ebbd095
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:26:22 2011 +0200
files:       tests/tools/test_tools.py
description:
updated test to take into account unregister handler in output


changeset:   2633:5c8732519a2e
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:27:22 2011 +0200
files:       circuits/core/components.py
description:
unregister event with no parameters unregisters all components


changeset:   2634:6bde802f1307
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:27:30 2011 +0200
files:       circuits/tools/__init__.py
description:
revert to unregistering directly for kill()


changeset:   2635:d8274eb06273
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:32:26 2011 +0200
files:       tests/core/test_manager_repr.py
description:
updated test to take into account unregister handler


changeset:   2636:cff090a5ec79
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 18:32:49 2011 +0200
files:       circuits/core/events.py
description:
default component to None in Unregister event


changeset:   2637:838d10bdeb68
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 20:02:33 2011 +0200
files:       circuits/core/components.py
description:
let components unregister by themselves, so that will fire an unregister event when unregistered


changeset:   2638:84041ab45e66
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 20:03:59 2011 +0200
files:       circuits/core/manager.py
description:
fixed bug in remove self._cmap and self._tmap handlers


changeset:   2639:37d85d578cf1
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 20:05:07 2011 +0200
files:       circuits/core/manager.py
description:
we handle the case of handlers while we are in the handlers loop, handleattrs goes missing so we continue the loop and skip that handler


changeset:   2640:9124f06c8117
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 20:05:35 2011 +0200
files:       tests/net/test_udp.py
description:
only unregister server in test_udp, removed debugger form test_udp


changeset:   2641:3069d03ed8aa
user:        Alessio Deiana <adeiana@gmail.com>
date:        Fri May 13 20:19:06 2011 +0200
files:       tests/web/test_main.py
description:
handle not found error in test_main


changeset:   2642:ebf8b964d3ae
user:        prologic
date:        Sat May 14 10:51:30 2011 +1000
files:       tests/web/test_main.py
description:
Fixed a NameError case in tests.web.test_main


changeset:   2643:ac7c220307f1
user:        prologic
date:        Sat May 14 10:53:51 2011 +1000
files:       circuits/core/components.py
description:
Backed out changeset 838d10bdeb68 - This breaks existsing behavior. Component graphs should be kept in trac when unregistering


changeset:   2644:01662a36170f
user:        prologic
date:        Sat May 14 11:29:03 2011 +1000
files:       circuits/core/manager.py
description:
Keep a local copy of handlers and handlerattrs in the local scope of the _dispatcher (which resolves a but exposed by test_udp_close)


changeset:   2645:59b0af12a6e5
user:        prologic
date:        Mon May 16 08:50:30 2011 +1000
files:       docs/source/start/requirements.rst
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2646:03df595c0c0b
user:        prologic
date:        Mon May 16 08:57:04 2011 +1000
files:       circuits/app/daemon.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2647:0532aec103a0
user:        prologic
date:        Mon May 16 09:11:57 2011 +1000
files:       circuits/app/env.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2648:00c685d9e42f
user:        prologic
date:        Mon May 16 09:15:08 2011 +1000
files:       circuits/app/startup.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2649:44ea8ebc8900
user:        prologic
date:        Mon May 16 09:16:49 2011 +1000
files:       circuits/core/components.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2650:872f479318a0
user:        prologic
date:        Mon May 16 09:17:55 2011 +1000
files:       circuits/core/debugger.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2651:7cd7c412e6fa
user:        prologic
date:        Mon May 16 09:23:30 2011 +1000
files:       circuits/core/events.py
description:
Updated docs :: Fixed some spelling mistakes


changeset:   2652:5b80d2bb7aee
user:        prologic
date:        Mon May 16 09:32:38 2011 +1000
files:       circuits/core/futures.py
description:
Updated docs :; Added some docs to the circuits.core.futures module docstring


changeset:   2653:abfaf35bd14a
user:        prologic
date:        Wed May 18 00:53:29 2011 +1000
files:       circuits/core/manager.py
description:
Possible fix for CPU usage problems when using circuits with no I/O pollers and using a Timer for timed events


changeset:   2654:49131fd3c2cc
user:        prologic
date:        Thu May 19 07:40:17 2011 +1000
files:       examples/telnet.py
description:
Remove use of custom channels in .fire calls


changeset:   2655:af129ca3063d
user:        prologic
date:        Wed Jun 01 08:40:25 2011 +1000
files:       circuits/core/manager.py tests/core/test_debugger.py
description:
Fixed a bug in Manager.tick(...) causing tick exceptions not to be handled properly


changeset:   2656:69db71154f44
tag:         tip
user:        prologic
date:        Wed Jun 01 09:04:59 2011 +1000
files:       circuits/core/manager.py
description:
Removed unnecessary outer try/except in Manager.tick()


