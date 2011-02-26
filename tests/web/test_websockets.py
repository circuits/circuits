#!/usr/bin/env python

from random import choice, randint

import pytest

from circuits import handler, Component
from circuits.net.sockets import Close, Write
from circuits.web.dispatchers import WebSockets
from circuits.web.client import Client, Connect, Request


def generate_key():
    spaces = randint(1, 12)
    maxnum = 4294967295 / spaces
    number = randint(0, maxnum)
    product = number * spaces
    key = str(product)
    available_chars = range(0x21, 0x2f + 1) + range(0x3a, 0x7e + 1)
    n = randint(1, 12)
    for _ in xrange(n):
        ch = choice(available_chars)
        pos = randint(0, len(key))
        key = key[0:pos] + chr(ch) + key[pos:]
    for _ in xrange(spaces):
        pos = randint(1, len(key) - 1)
        key = key[0:pos] + " " + key[pos:]
    return number, key


def generate_key3():
    return "".join([chr(randint(0, 255)) for _ in xrange(8)])


class Echo(Component):

    channel = "ws"

    def message(self, sock, data):
        self.push(Write(sock, data))


class WebSocketsClient(Component):

    channel = "web"

    def __init__(self, url):
        super(WebSocketsClient, self).__init__()

        self._buffer = ""
        self._handshake = False
        self._messages = []

        self._client = Client(url).register(self)

    def _parse_messages(self):
        msgs = []
        end_idx = 0
        buf = self._buffer
        while buf:
            frame_type = ord(buf[0])
            if frame_type == 0:
                # Normal message.
                end_idx = buf.find("\xFF")
                if end_idx == -1:  # pragma NO COVER
                    break
                msgs.append(buf[1:end_idx].decode("utf-8", "replace"))
                buf = buf[(end_idx + 1):]
            elif frame_type == 255:
                # Closing handshake.
                assert ord(buf[1]) == 0, \
                        "Unexpected closing handshake: %r" % buf
                self.closed = True
                break
            else:
                raise ValueError(
                    "Don't understand how to parse "
                    "this type of message: %r" % buf)
        self._buffer = buf
        return msgs

    @property
    def connected(self):
        if hasattr(self, "_client"):
            return self._client.connected

    @handler("read", filter=True, target="client")
    def _on_client_read(self, data):
        if self._handshake:
            self._buffer += data
            self._messages.extend(self._parse_messages())
            return True

    @handler("response")
    def _on_response(self, response):
        if (response.status == 101
                and response.message == "WebSocket Protocol Handshake"):
            self._handshake = True


def test(webapp):
    Echo().register(webapp)
    WebSockets("/websocket").register(webapp)

    client = WebSocketsClient(webapp.server.base)
    client.start()

    client.push(Connect())
    assert pytest.wait_for(client, "connected")

    number1, key1 = generate_key()
    number2, key2 = generate_key()
    body = generate_key3()

    method = "GET"
    url = "/websocket"
    headers = {
            "Upgrade": "WebSocket",
            "Connection": "Upgrade",
            "Host": "127.0.0.1:8000",
            "Origin": "http://127.0.0.1:8000",
            "Sec-WebSocket-Key1": key1,
            "Sec-WebSocket-Key2": key2,
    }

    client.push(Request(method, url, body, headers))
    assert pytest.wait_for(client, "_handshake")

    response = client._client.response
    assert response.status == 101
    assert response.message == "WebSocket Protocol Handshake"

    client.push(Write("\x00Hello World!\xff"))

    def test(obj, attr):
        messages = getattr(obj, attr)
        return messages and messages[0] == "Hello World!"

    assert pytest.wait_for(client, "_messages", test)

    client.push(Close())
    assert pytest.wait_for(client, "connected", False)

    client.stop()
