#!/usr/bin/env python
import os
import ssl
import sys
import tempfile
from os import path
from socket import gaierror

import pytest
from pytest import fixture

from circuits import Component
from circuits.web import BaseServer, Controller, Server

from .helpers import URLError, urlopen

CERTFILE = path.join(path.dirname(__file__), "cert.pem")


# self signed cert
if pytest.PYVER >= (2, 7, 9):
    SSL_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE


@fixture
def tmpfile(request):
    tmpdir = tempfile.mkdtemp()
    filename = os.path.join(tmpdir, "test.sock")

    return filename


class BaseRoot(Component):

    channel = "web"

    def request(self, request, response):
        return "Hello World!"


class Root(Controller):

    def index(self):
        return "Hello World!"


class MakeQuiet(Component):

    channel = "web"

    def ready(self, event, *args):
        event.stop()


def test_baseserver(manager, watcher):
    server = BaseServer(0).register(manager)
    MakeQuiet().register(server)
    watcher.wait("ready")

    BaseRoot().register(server)
    watcher.wait("registered")

    try:
        f = urlopen(server.http.base)
    except URLError as e:
        if isinstance(e.reason, gaierror):
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"

    server.unregister()
    watcher.wait("unregistered")


def test_server(manager, watcher):
    server = Server(0).register(manager)
    MakeQuiet().register(server)
    watcher.wait("ready")

    Root().register(server)

    try:
        f = urlopen(server.http.base)
    except URLError as e:
        if isinstance(e.reason, gaierror):
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"

    server.unregister()
    watcher.wait("unregistered")


@pytest.mark.skipif((2,) < sys.version_info < (3, 4, 3),
                    reason="Context not implemented under python 3.4.3")
@pytest.mark.skipif(sys.version_info < (2, 7, 9),
                    reason="Context not implemented under python 2.7.9")
def test_secure_server(manager, watcher):
    pytest.importorskip("ssl")

    server = Server(0, secure=True, certfile=CERTFILE).register(manager)
    MakeQuiet().register(server)
    watcher.wait("ready")

    Root().register(server)

    try:
        f = urlopen(server.http.base, context=SSL_CONTEXT)
    except URLError as e:
        if isinstance(e.reason, gaierror):
            f = urlopen("http://127.0.0.1:9000")
        else:
            raise

    s = f.read()
    assert s == b"Hello World!"

    server.unregister()
    watcher.wait("unregistered")


def test_unixserver(manager, watcher, tmpfile):
    if pytest.PLATFORM == "win32":
        pytest.skip("Unsupported Platform")

    server = Server(tmpfile).register(manager)
    MakeQuiet().register(server)
    assert watcher.wait("ready")

    Root().register(server)

    assert path.basename(server.host) == "test.sock"

    try:
        from uhttplib import UnixHTTPConnection

        client = UnixHTTPConnection(server.http.base)
        client.request("GET", "/")
        response = client.getresponse()
        s = response.read()

        assert s == b"Hello World!"
    except ImportError:
        pass

    server.unregister()
    watcher.wait("unregistered")


@pytest.mark.skipif((2, 7, 9) < sys.version_info < (3, 4, 3),
                    reason="Context not implemented under python 3.4.3")
@pytest.mark.skipif(sys.version_info < (2, 7, 9),
                    reason="Context not implemented under python 2.7.9")
def test_multi_servers(manager, watcher):
    pytest.importorskip("ssl")

    insecure_server = Server(0, channel="insecure")
    secure_server = Server(
        0,
        channel="secure", secure=True, certfile=CERTFILE
    )

    server = (insecure_server + secure_server).register(manager)
    MakeQuiet().register(server)
    watcher.wait("ready")

    Root().register(server)

    f = urlopen(insecure_server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    f = urlopen(secure_server.http.base, context=SSL_CONTEXT)
    s = f.read()
    assert s == b"Hello World!"

    server.unregister()
    watcher.wait("unregistered")
