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
try:
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import urlunsplit
from collections import defaultdict

from circuits.net.sockets import Write
from circuits import handler, BaseComponent, Event


class MalformedWebSocket(ValueError):
    """Malformed WebSocket Error"""


class Message(Event):
    """Message Event"""


class WebSocketsMediator(BaseComponent):

    channel = "ws"

    @handler("write")
    def _on_write(self, sock, data):
        payload = b'\x00' + data.encode("utf-8") + b'\xff'
        self.fire(Write(sock, payload), self.parent.channel)

    @handler("message_value_changed")
    def _on_message_value_changed(self, value):
        sock, message = value.event.args
        result, data = value.result, value.value
        if result and isinstance(data, basestring):
                self.fire(Write(sock, data))


class WebSockets(BaseComponent):

    channel = "web"

    def __init__(self, path=None, wschannel="ws"):
        super(WebSockets, self).__init__()

        self.path = path
        self.wschannel = wschannel

        self._clients = []
        self._buffers = defaultdict(bytes)

        WebSocketsMediator(channel=wschannel).register(self)

    def _parse_messages(self, sock):
        msgs = []
        end_idx = 0
        buf = self._buffers[sock]
        while buf:
            frame_type = buf[0] if isinstance(buf[0], int) else ord(buf[0])
            if frame_type == 0:
                # Normal message.
                end_idx = buf.find(b"\xFF")
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

    @handler("disconnect")
    def _on_disconnect(self, sock):
        if sock in self._clients:
            self._clients.remove(sock)
        if sock in self._buffers:
            del self._buffers[sock]

    @handler("read", filter=True)
    def _on_read(self, sock, data):
        if sock in self._clients:
            self._buffers[sock] += data
            messages = self._parse_messages(sock)
            for message in messages:
                value = self.fire(Message(sock, message), self.wschannel)
                value.notify = True
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
