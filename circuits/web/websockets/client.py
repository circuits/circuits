import base64
import os
import random
from errno import ECONNRESET
from socket import error as SocketError

from circuits.core.components import BaseComponent
from circuits.core.handlers import handler
from circuits.net.events import close, connect, write
from circuits.net.sockets import TCPClient
from circuits.protocols.http import HTTP
from circuits.protocols.websocket import WebSocketCodec
from circuits.six.moves.urllib_parse import urlparse
from circuits.web.client import NotConnected
from circuits.web.headers import Headers


class WebSocketClient(BaseComponent):

    """
    An RFC 6455 compliant WebSocket client component. Upon receiving a
    :class:`circuits.web.client.Connect` event, the component tries to
    establish the connection to the server in a two stage process. First, a
    :class:`circuits.net.events.connect` event is sent to a child
    :class:`~.sockets.TCPClient`. When the TCP connection has been established,
    the HTTP request for opening the WebSocket is sent to the server.
    A failure in this setup process is signaled by raising an
    :class:`~.client.NotConnected` exception.

    When the server accepts the request, the WebSocket connection is
    established and can be used very much like an ordinary socket
    by handling :class:`~.net.events.read` events on and sending
    :class:`~.net.events.write` events to the channel
    specified as the ``wschannel`` parameter of the constructor. Firing
    a :class:`~.net.events.close` event on that channel closes the
    connection in an orderly fashion (i.e. as specified by the
    WebSocket protocol).
    """

    channel = "wsclient"

    def __init__(self, url, channel=channel, wschannel="ws", headers=None):
        """
        :param url: the URL to connect to.
        :param channel: the channel used by this component
        :param wschannel: the channel used for the actual WebSocket
            communication (read, write, close events)
        :param headers: additional headers to be passed with the
            WebSocket setup HTTP request
        """
        super(WebSocketClient, self).__init__(channel=channel)

        self._url = url
        self._headers = headers or {}
        self._response = None
        self._pending = 0
        self._wschannel = wschannel

        self._transport = TCPClient(channel=self.channel).register(self)
        HTTP(channel=self.channel).register(self._transport)

    @handler("ready")
    def _on_ready(self, event, *args, **kwargs):
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
            raise NotConnected()
        self._resource = p.path or "/"
        if p.query:
            self._resource += "?" + p.query
        self.fire(connect(self._host, self._port, self._secure),
                  self._transport)

    @handler("connected")
    def _on_connected(self, host, port):
        headers = Headers([(k, v) for k, v in self._headers.items()])
        # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
        if "Host" not in headers:
            headers["Host"] = self._host \
                + (":" + str(self._port)) if self._port else ""
        headers["Upgrade"] = "websocket"
        headers["Connection"] = "Upgrade"
        try:
            sec_key = os.urandom(16)
        except NotImplementedError:
            sec_key = "".join([chr(random.randint(0, 255)) for i in range(16)])
        headers[
            "Sec-WebSocket-Key"] = base64.b64encode(sec_key).decode("latin1")
        headers["Sec-WebSocket-Version"] = "13"
        command = "GET %s HTTP/1.1" % self._resource
        message = "%s\r\n%s" % (command, headers)
        self._pending += 1
        self.fire(write(message.encode('utf-8')), self._transport)
        return True

    @handler("response")
    def _on_response(self, response):
        self._response = response
        self._pending -= 1
        if response.headers.get("Connection", "").lower() == "close" \
                or response.status != 101:
            self.fire(close(), self._transport)
            raise NotConnected()
        WebSocketCodec(
            data=response.body.read(), channel=self._wschannel).register(self)

    @handler("error", priority=10)
    def _on_error(self, event, error, *args, **kwargs):
        # For HTTP 1.1 we leave the connection open. If the peer closes
        # it after some time and we have no pending request, that's OK.
        if isinstance(error, SocketError) and error.args[0] == ECONNRESET \
                and self._pending == 0:
            event.stop()

    def close(self):
        if self._transport is not None:
            self._transport.close()

    @property
    def connected(self):
        return getattr(self._transport, "connected", False) \
            if hasattr(self, "_transport") else False
