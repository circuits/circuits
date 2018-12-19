# -*- coding: utf-8 -*-
""" Tests for StompClient component """
from __future__ import print_function

import os
import ssl

import pytest

from circuits import Component
from circuits.protocols.stomp.events import (
    connect, disconnect, send, subscribe,
)

try:
    from circuits.protocols.stomp.client import StompClient, ACK_AUTO
except ImportError:
    pytest.importorskip("stompest")


URI = os.environ.get("TEST_STOMP_URI", "")
LOGIN = os.environ.get("TEST_STOMP_LOGIN", "")
PASSCODE = os.environ.get("TEST_STOMP_PASSWORD", "")
HOST = os.environ.get("TEST_STOMP_HOST", "")
QUEUE = os.environ.get("TEST_STOMP_QUEUE", "")
TEST_MESSAGE = u"Test Message"
PROXY_HOST = os.environ.get("TEST_STOMP_PROXY_HOST", "")
try:
    PROXY_PORT = int(os.environ.get("TEST_STOMP_PROXY_PORT", 0))
except ValueError:
    PROXY_PORT = None


# Tests can only run if a STOMP server is available
needstomp = pytest.mark.skipif(not(all((URI, LOGIN, PASSCODE, HOST, QUEUE))),
                               reason="No STOMP Server Configured")
needproxy = pytest.mark.skipif(not(PROXY_HOST and PROXY_PORT),
                               reason="No HTTP Proxy Configured")


class App(Component):
    def __init__(self, queue, host=None, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.queue = QUEUE
        self.host = HOST
        self.received = []

    def connected(self):
        self.fire(subscribe(self.queue, ack=ACK_AUTO))
        print("connected")

    def message(self, event, headers, message):
        self.received.append(message)
        print("received")

    def subscribe_success(self, *args, **kwargs):
        print("subscribed")

    def disconnected(self, *args, **kwargs):
        print("disconnected")


@needstomp
@pytest.mark.parametrize("context",
                         [ssl.create_default_context(), None])
def test_stomp_ssl(manager, watcher, tmpdir, context):
    """ test ssl connection """
    port = 61614

    if context:
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
    else:
        # Run like older Python version w/out ssl context
        pass

    app = App(QUEUE).register(manager)
    client = StompClient(URI, port,
                         username=LOGIN,
                         password=PASSCODE,
                         ssl_context=context).register(app)

    watcher.wait("registered")
    client.fire(connect(host=HOST))
    watcher.wait("connected")

    client.fire(subscribe(QUEUE, ack=ACK_AUTO))
    watcher.wait("subscribe_success")

    client.fire(send(headers=None,
                     body=TEST_MESSAGE,
                     destination=QUEUE))
    watcher.wait("message_success")
    client.fire(disconnect())
    received = app.received[0].decode()
    assert received == TEST_MESSAGE

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")


@needstomp
def test_stomp_no_ssl(manager, watcher, tmpdir):
    """ Test plain tcp connection """
    port = 61613

    app = App(QUEUE).register(manager)
    client = StompClient(URI, port,
                         username=LOGIN,
                         password=PASSCODE,
                         use_ssl=False).register(app)

    watcher.wait("registered")
    client.fire(connect(host=HOST))
    app.wait("connected")

    client.fire(subscribe(QUEUE, ack=ACK_AUTO))
    watcher.wait("subscribe_success")

    client.fire(send(headers=None,
                body=TEST_MESSAGE,
                destination=QUEUE))
    watcher.wait("message_success")
    client.fire(disconnect())
    received = app.received[0].decode()
    assert received == TEST_MESSAGE

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")


@needstomp
@needproxy
@pytest.mark.parametrize("context",
                         [ssl.create_default_context(), None])
def test_stomp_proxy_ssl(manager, watcher, tmpdir, context):
    """ test ssl connection through http proxy"""
    port = 61614

    if context:
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
    else:
        # Run like older Python version w/out ssl context
        pass

    app = App(QUEUE).register(manager)
    client = StompClient(URI, port,
                         username=LOGIN,
                         password=PASSCODE,
                         proxy_host=PROXY_HOST,
                         proxy_port=PROXY_PORT,
                         ssl_context=context).register(app)

    watcher.wait("registered")
    client.fire(connect(host=HOST))
    watcher.wait("connected")

    client.fire(subscribe(QUEUE, ack=ACK_AUTO))
    watcher.wait("subscribe_success")

    client.fire(send(headers=None,
                     body=TEST_MESSAGE,
                     destination=QUEUE))
    watcher.wait("message_success")
    client.fire(disconnect())
    received = app.received[0].decode()
    assert received == TEST_MESSAGE

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")


@needstomp
@needproxy
def test_stomp_proxy_no_ssl(manager, watcher, tmpdir):
    """ Test plain tcp connection through http proxy"""
    port = 61613

    app = App(QUEUE).register(manager)
    client = StompClient(URI, port,
                         username=LOGIN,
                         password=PASSCODE,
                         proxy_host=PROXY_HOST,
                         proxy_port=PROXY_PORT,
                         use_ssl=False).register(app)

    watcher.wait("registered")
    client.fire(connect(host=HOST))
    app.wait("connected")

    client.fire(subscribe(QUEUE, ack=ACK_AUTO))
    watcher.wait("subscribe_success")

    client.fire(send(headers=None,
                body=TEST_MESSAGE,
                destination=QUEUE))
    watcher.wait("message_success")
    client.fire(disconnect())
    received = app.received[0].decode()
    assert received == TEST_MESSAGE

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")
