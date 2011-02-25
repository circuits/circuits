#!/usr/bin/env python

from struct import pack
from hashlib import md5
from collections import defaultdict

from circuits.web import Logger, Server, Static
from circuits import handler, BaseComponent, Event

from circuits import Debugger


class MalformedWebSocket(ValueError):
    """Malformed WebSocket Error"""


class WebSocketEvent(Event):
    """WebSocket Event"""


class WebSocketRequest(WebSocketEvent):
    """WebSocket Request Event"""

    channel = "websocket_request"


class Message(WebSocketEvent):
    """Message Event"""


class WebSockets(BaseComponent):

    channel = "web"

    def __init__(self, path=None):
        super(WebSockets, self).__init__()

        self.path = path

        self._clients = []
        self._buffers = defaultdict(str)

    def _parse_messages(self, sock):
        msgs = []
        end_idx = 0
        buf = self._buffers[sock]
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
        self._buffers[sock] = buf
        return msgs

    @handler("read", filter=True)
    def _on_read(self, sock, data):
        if sock in self._clients:
            self._buffers[sock] += data
            messages = self._parse_messages(sock)
            for message in messages:
                self.push(Message(sock, message))
            return True

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self.path is not None and not request.path.startswith(self.path):
            return

        headers = request.headers

        key1 = headers["Sec-WebSocket-Key1"]
        key2 = headers["Sec-WebSocket-Key2"]

        # Count spaces
        nums1 = key1.count(" ")
        nums2 = key2.count(" ")

        # Join digits in the key
        num1 = ''.join([x for x in key1 if x.isdigit()])
        num2 = ''.join([x for x in key2 if x.isdigit()])

        # Divide the digits by the num of spaces
        key1 = int(int(num1) / int(nums1))
        key2 = int(int(num2) / int(nums2))

        # Pack into Network byte ordered 32 bit ints
        key1 = pack("!I", key1)
        key2 = pack("!I", key2)

        # Concat key1, key2, and the the body of the client handshake
        # and take the md5 sum of it
        key = key1 + key2 + request.body.read()
        m = md5()
        m.update(key)
        d = m.digest()

        del response.headers["Content-Type"]

        response.code = 101
        response.message = "WebSocket Protocol Handshake"
        response.headers["Upgrade"] = "WebSocket"
        response.headers["Connection"] = "Upgrade"
        response.headers["Sec-WebSocket-Origin"] = "http://127.0.0.1:8888"
        response.headers["Sec-WebSocket-Location"] = \
                "ws://localhost:8888/websocket"
        response.headers["Sec-WebSocket-Protocol"] = "chat"

        self._clients.append(request.sock)

        response.close = False

        return d

(Server(("127.0.0.1", 8888))
    + WebSockets("/websocket")
    + Debugger()
    + Static()
    + Logger()
).run()
