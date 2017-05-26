# -*- coding: utf-8 -*-
from __future__ import print_function
import ssl
import pytest

from circuits import Component, handler
from circuits.protocols.stomp.events import *

try:
    from circuits.protocols.stomp.client import StompClient, ACK_AUTO
except ImportError:
    pytest.importorskip("stompest")


uri = "orangutan.rmq.cloudamqp.com"
login = "cjferxig"
passcode="5fyrCArVx4RY6mAwUiM7Mbd_FEnwYwUU"
host = "cjferxig"
queue = "test1"
test_message = u"Test Message"

class App(Component):
    def __init__(self, queue, host=None, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.queue = queue
        self.host=host
        self.received = []

    def Connected(self):
        self.fire(Subscribe(self.queue, ack=ACK_AUTO))
        print("connected")

    def Message(self, event, headers, message):
        self.received.append(message)
        print("received")

    def Subscribe_success(self, *args, **kwargs):
        print("subscribed")

    def Disconnected(self, *args, **kwargs):
        print("disconnected")


def test_stomp_ssl(manager, watcher, tmpdir):
    """ test ssl connection """
    port = 61614

    try:
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
    except:
        # Older Python version w/out ssl context
        context = None

    app = App(queue).register(manager)
    client = StompClient(uri, port,
                         username=login,
                         password=passcode,
                         ssl_context=context).register(app)

    watcher.wait("registered")
    client.fire(Connect(host=host))
    watcher.wait("Connected")
    
    client.fire(Subscribe(queue, ack=ACK_AUTO))
    watcher.wait("Subscribe_success")

    client.fire(Send(headers=None,
                     body=test_message,
                     destination=queue))
    watcher.wait("Message_success")
    client.fire(Disconnect())
    received = app.received[0].decode()
    assert received == test_message

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")

def test_stomp_no_ssl(manager, watcher, tmpdir):
    """ Test plain tcp connection """
    port = 61613

    app = App(queue).register(manager)
    client = StompClient(uri, port,
                         username=login,
                         password=passcode,
                         use_ssl=False).register(app)

    watcher.wait("registered")
    client.fire(Connect(host=host))
    app.wait("Connected")
    
    client.fire(Subscribe(queue, ack=ACK_AUTO))
    watcher.wait("Subscribe_success")

    client.fire(Send(headers=None,
                  body=test_message,
                  destination=queue))
    watcher.wait("Message_success")
    client.fire(Disconnect())
    received = app.received[0].decode()
    assert received == test_message

    client.unregister()
    app.unregister()
    watcher.wait("unregistered")
