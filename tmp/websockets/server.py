#!/usr/bin/env python

import collections
import select
import string
import struct
from errno import EAGAIN
try:
    from hashlib import md5
except ImportError: #pragma NO COVER
    from md5 import md5
from errno import EINTR
from socket import error as SocketError

from circuits.core.utils import findcmp
from circuits.core.pollers import _Poller
from circuits.web import Logger, Server, Static
from circuits import handler, BaseComponent, Event

from circuits import Debugger

def _extract_number(value):
    out = ""
    spaces = 0
    for char in value:
        if char in string.digits:
            out += char
        elif char == " ":
            spaces += 1
    return int(out) / spaces

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
        self._buffers = {}

    def _parse_messages(self, sock):
        msgs = []
        end_idx = 0
        buf = self._buffers[sock]
        while buf:
            frame_type = ord(buf[0])
            if frame_type == 0:
                # Normal message.
                end_idx = buf.find("\xFF")
                if end_idx == -1: #pragma NO COVER
                    break
                msgs.append(buf[1:end_idx].decode("utf-8", "replace"))
                buf = buf[end_idx+1:]
            elif frame_type == 255:
                # Closing handshake.
                assert ord(buf[1]) == 0, "Unexpected closing handshake: %r" % buf
                self.closed = True
                break
            else:
                raise ValueError(
                    "Don't understand how to parse "
                    "this type of message: %r" % buf)
        self._buffers[sock] = buf
        return msgs

    @handler("read", filter=True)
    def _on_read(self, sock):
        if sock in self._clients:
            self._buffers[sock] += data
            messages = self._parse_messages(sock)
            for message in messages:
                self.push(Message(sock, message))
            return True

    @handler("websocket_request")
    def _on_websocket_request(self, request, response):
        headers = request.headers

        if headers.get("Connection", None) == "Upgrade" and \
            headers.get("Upgrade", None) == "WebSocket":

            # See if they sent the new-format headers
            if "Sec_WebSocket-Key1" in headers:
                protocol_version = 76
                if "Sec-WebSocket-Key2" not in headers:
                    raise MalformedWebSocket()
            else:
                protocol_version = 75

            # If it"s new-version, we need to work out our challenge response
            if protocol_version == 76:
                key1 = _extract_number(headers["Sec-WebSocket-Key1"])
                key2 = _extract_number(headers["Sec-WebSocket-Key2"])
                # There"s no content-length header in the request, but it has 8
                # bytes of data.
                key3 = request.body.read()
                key = struct.pack(">II", key1, key2) + key3
                handshake_response = md5(key).digest()

            location = "ws://%s:%s%s" % (request.host,
                    request.local.port, request.path)
            qs = request.qs
            if qs:
                location += "?" + qs

            if protocol_version == 75:
                response.status = (101, "Web Socket Protocol Handshake")
                response.headers["Upgrade"] =  "WebSocket"
                response.headers["Connection"] =  "Upgrade"
                response.headers["WebSocket-Origin"] = headers["Origin"]
                response.headers["WebSocket-Location"] =  location
            elif protocol_version == 76:
                response.status = (101, "Web Socket Protocol Handshake")
                response.headers["Upgrade"] =  "WebSocket"
                response.headers["Connection"] =  "Upgrade"

                response.headers["Sec-WebSocket-Origin"] = headers["Origin"]

                response.headers["Sec-WebSocket-Protocol"] = \
                        headers.get("Sec-WebSocket-Protocol", "default")
                        
                response.headers["Sec-WebSocket-Location"] = location
            else:
                raise MalformedWebSocket("Unknown WebSocket protocol version.")

            socket = request.sock
            self._clients.append(request.sock)

            response.stream = True
            response.close = False

            return response

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self.path is not None and not request.path.startswith(self.path):
            return

        return self.push(WebSocketRequest(request, response))

(Server(("0.0.0.0", 8000))
    + WebSockets("/websocket")
    + Debugger()
    + Static()
    + Logger()
).run()
