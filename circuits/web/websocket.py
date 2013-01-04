"""
.. codeauthor: mnl
"""
from circuits.web.headers import Headers
from circuits.core.handlers import handler
import os
import random
import base64
from circuits.web import client
from circuits.net.protocols.websocket import WebSocketCodec
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from circuits.core.components import BaseComponent
from circuits.web.client import NotConnected
from circuits.net.sockets import TCPClient, Connect, Write, Close
from circuits.net.protocols.http import HTTP
from socket import error as SocketError
from errno import ECONNRESET

class WebSocketClient(BaseComponent):
    """
    A WebSocket client component.
    """
    
    channel = "web-ws"
    
    def __init__(self, url, channel=channel, wschannel="ws", headers={}):
        super(WebSocketClient, self).__init__(channel=channel)

        self._url = url
        self._headers = headers
        self._response = None
        self._pending = 0
        self._wschannel = wschannel

        self._transport = TCPClient(channel=self.channel).register(self)
        HTTP(channel=self.channel).register(self._transport)
        
    @handler("connect", priority=0.1, filter=True)
    def _on_connect(self, event, *args, **kwargs):
        if not isinstance(event, client.Connect):
            return
        p = urlparse(self._url)
        if not p.hostname:
            raise ValueError("URL must be absolute")
        self._host = p.hostname
        if p.scheme == "ws":
            self._secure = False
            self._port = p.port or 80
        elif p.scheme == "wss":
            self._secure = True
            self._port = p.port or 443
        else:
            self.fire(NotConnected())
            return
        self._resource = p.path or "/"
        if p.query:
            self._resource += "?" + p.query
        self.fire(Connect(self._host, self._port, self._secure),
                  self._transport)
        headers = Headers([(k, v) for k, v in self._headers.items()])
        # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
        if not headers.has_key("Host"):
            headers["Host"] = self._host \
                + (":" + str(self._port)) if self._port else ""
        headers["Upgrade"] = "websocket"
        headers["Connection"] = "Upgrade"
        try:
            sec_key = os.urandom(16)
        except NotImplementedError:
            sec_key = "".join([chr(random.randint(0,255)) for i in range(16)])
        headers["Sec-WebSocket-Key"] = base64.b64encode(sec_key)
        headers["Sec-WebSocket-Version"] = "13"
        command = "GET %s HTTP/1.1" % self._resource
        message = "%s\r\n%s" % (command, headers)
        self._pending += 1
        self.fire(Write(message.encode('utf-8')), self._transport)
        return True

    @handler("response")
    def _on_response(self, response):
        self._response = response
        self._pending -= 1
        if response.headers.get("Connection") == "Close" \
            or response.status != 101:
            self.fire(Close(), self._transport)
        WebSocketCodec(channel=self._wschannel).register(self)

    @handler("error", filter=True, priority=10)
    def _on_error(self, error, *args, **kwargs):
        # For HTTP 1.1 we leave the connection open. If the peer closes
        # it after some time and we have no pending request, that's OK.
        if isinstance(error, SocketError) and error.args[0] == ECONNRESET \
            and self._pending == 0:
            return True

    def close(self):
        if self._transport != None:
            self._transport.close()

    @property
    def connected(self):
        return getattr(self._transport, "connected", False) \
            if hasattr(self, "_transport") else False
