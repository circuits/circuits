# Module:   websockets
# Date:     26th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au
from circuits.web.errors import HTTPError
from circuits.net.protocols.websocket import WebSocketCodec

"""WebSockets

This module implements a WebSockets dispatcher that handles the
WebSockets handshake, upgrades the connection and translates incoming
messages into ``Message`` events.
"""

import hashlib
import base64
try:
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import urlunsplit

from circuits.net.sockets import Write
from circuits import handler, BaseComponent


class MalformedWebSocket(ValueError):
    """Malformed WebSocket Error"""


class WebSockets(BaseComponent):

    channel = "web"

    def __init__(self, path=None, wschannel="ws"):
        super(WebSockets, self).__init__()

        self._path = path
        self._wschannel = wschannel
        self._codecs = dict()

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self._path is not None and not request.path.startswith(self._path):
            return

        self._protocol_version = 13 
        headers = request.headers
        sec_key = headers.get("Sec-WebSocket-Key", None)
        connection_tokens = [s.strip() for s in \
                             headers.get("Connection", "").lower().split(",")]
        
        if not headers.has_key("Host") \
            or headers.get("Upgrade", "").lower() != "websocket" \
            or not "upgrade" in connection_tokens \
            or sec_key is None \
            or len(base64.b64decode(sec_key)) != 16:
            return HTTPError(request, response, code=400)
        if headers.get("Sec-WebSocket-Version", "") != "13":
            response.headers["Sec-WebSocket-Version"] = "13"
            return HTTPError(request, response, code=400)
        
        # Generate accept header information
        msg = sec_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        hasher = hashlib.sha1()
        hasher.update(msg)
        accept = base64.b64encode(hasher.digest())

        # Successful completion
        response.code = 101
        response.close = False
        del response.headers["Content-Type"]
        response.headers["Upgrade"] = "WebSocket"
        response.headers["Connection"] = "Upgrade"
        response.headers["Sec-WebSocket-Accept"] = accept 
        response.message = "WebSocket Protocol Handshake"
        codec = WebSocketCodec(request.sock, channel=self._wschannel)
        self._codecs[request.sock] = codec
        codec.register(self)
        return ""
        
    @handler("disconnect")
    def _on_disconnect(self, sock):
        if self._codecs.has_key(sock):
            del self._codecs[sock]

