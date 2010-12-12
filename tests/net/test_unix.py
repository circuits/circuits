#!/usr/bin/env python

import os
import sys

import py

if sys.platform in ("win32", "cygwin"):
    py.test.skip("Test Not Applicable on Windows")

from circuits.core import pollers
from circuits.core.pollers import Select
from circuits.net.sockets import Close, Connect, Write
from circuits.net.sockets import UNIXServer, UNIXClient

from client import Client
from server import Server

def pytest_generate_tests(metafunc):
    metafunc.addcall(funcargs={"poller": Select})
    if pollers.HAS_POLL:
        from circuits.core.pollers import Poll
        metafunc.addcall(funcargs={"poller": Poll})
    if pollers.HAS_EPOLL:
        from circuits.core.pollers import EPoll
        metafunc.addcall(funcargs={"poller": EPoll})

def test_unix(tmpdir, poller):
    sockpath = tmpdir.ensure("test.sock")
    filename = str(sockpath)
    server = Server() + UNIXServer(filename, poller=poller)
    client = Client() + UNIXClient(poller=poller)

    server.start()
    client.start()

    try:
        client.push(Connect(filename))
        py.test.wait_for(client, "connected")
        py.test.wait_for(server, "connected")
        py.test.wait_for(client, "data", "Ready")

        client.push(Write("foo"))
        py.test.wait_for(server, "data", "foo")

        client.push(Close())
        server.push(Close())
        py.test.wait_for(client, "disconnected")
        py.test.wait_for(server, "disconnected")
    finally:
        server.stop()
        client.stop()
        os.remove(filename)
