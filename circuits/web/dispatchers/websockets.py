# Module:   websockets
# Date:     26th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WebSockets

This module implements a WebSockets dispatcher that handles the
WebSockets handshake, upgrades the connection and translates incoming
messages into ``Message`` events.
"""

from struct import pack
from hashlib import md5
from urlparse import urlunsplit
from collections import defaultdict

from circuits.net.sockets import Write
from circuits import handler, BaseComponent, Event


class MalformedWebSocket(ValueError):
    """Malformed WebSocket Error"""


class WebSocketEvent(Event):
    """WebSocket Event"""

    _target = "ws"


class Message(WebSocketEvent):
    """Message Event"""

    target = WebSocketEvent._target


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

    @handler("disconnect", target="web")
    def _on_disconnect(self, sock):
        if sock in self._clients:
            self._clients.remove(sock)
        if sock in self._buffers:
            del self._buffers[sock]

    @handler("write", target="ws")
    def _on_write(self, sock, data):
        payload = chr(0x00) + data.encode("utf-8") + chr(0xFF)
        self.push(Write(sock, payload))

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

        origin = headers["Origin"]
        location = urlunsplit(("ws", headers["Host"], self.path, "", ""))

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
        response.headers["Sec-WebSocket-Origin"] = origin
        response.headers["Sec-WebSocket-Location"] = location

        self._clients.append(request.sock)

        response.close = False

        return d
