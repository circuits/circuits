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

* Fixes a missing Event ``Closed()`` not being triggered for ``UDPServer``.
* Make underlying ``UDPServer`` socket reuseable by setting ``SO_REUSEADDR``
* Fixes Server socket being discarded twice on close + disconnect
* Socket.write now expects bytes (bytes for python3 and str for python2)
* Better handling of encoding in HTTP Component (allow non utf-8 encoding)
* Always encode http headers in utf-8
* Fixes error after getting socket.ERRCONNREFUSED
* Allows TCPClient to bind to a specific port
* Addes deprecation warnings for .push .add and .remove methods
* Improved docs
* Addes a ticks limit to waitEvent
* Handles closing of udpserver socket when no client is connected
* Adds an unregister handler for components
* Allows utils.kill to work from a different thread
* Fixes bug when handling "*" in channels and targets
* Fixes a bug that could occur when unregistering components
* Fixes for CPU usage problems when using circuits with no I/O pollers and using a Timer for timed events
