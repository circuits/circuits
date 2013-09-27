# Module:   dispatcher
# Date:     26th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

import base64
import hashlib

from circuits.tools import deprecated
from circuits.net.events import connect
from circuits.web.errors import httperror
from circuits import handler, BaseComponent
from circuits.protocols.websocket import WebSocketCodec


class WebSocketsDispatcher(BaseComponent):
    """
    This class implements an RFC 6455 compliant WebSockets dispatcher
    that handles the WebSockets handshake and upgrades the connection.

    The dispatcher listens on its channel for :class:`~.web.events.Request`
    events and tries to match them with a given path. Upon a match,
    the request is checked for the proper Opening Handshake information.
    If successful, the dispatcher confirms the establishment of the
    connection to the client. Any subsequent data from the client is
    handled as a WebSocket data frame, decoded and fired as
    a :class:`~.sockets.Read` event on the ``wschannel`` passed to
    the constructor. The data from :class:`~.net.events.write` events on
    that channel is encoded as data frames and forwarded to the client.

    Firing a :class:`~.sockets.Close` event on the ``wschannel`` closes the
    connection in an orderly fashion (i.e. as specified by the
    WebSocket protocol).
    """

    channel = "web"

    def __init__(self, path=None, wschannel="ws", *args, **kwargs):
        """
        :param path: the path to handle. Requests that start with this
            path are considered to be WebSocket Opening Handshakes.

        :param wschannel: the channel on which :class:`~.sockets.read`
            events from the client will be delivered and where
            :class:`~.net.events.write` events to the client will be
            sent to.
        """

        super(WebSocketsDispatcher, self).__init__(*args, **kwargs)

        self._path = path
        self._wschannel = wschannel
        self._codecs = dict()

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self._path is not None and not request.path.startswith(self._path):
            return

        self._protocol_version = 13
        headers = request.headers
        sec_key = headers.get("Sec-WebSocket-Key", "").encode("utf-8")
        connection_tokens = [s.strip() for s in
                             headers.get("Connection", "").lower().split(",")]

        if (not "Host" in headers
            or headers.get("Upgrade", "").lower() != "websocket"
            or not "upgrade" in connection_tokens
            or sec_key is None
                or len(base64.b64decode(sec_key)) != 16):
                return httperror(request, response, code=400)
        if headers.get("Sec-WebSocket-Version", "") != "13":
            response.headers["Sec-WebSocket-Version"] = "13"
            return httperror(request, response, code=400)

        # Generate accept header information
        msg = sec_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        hasher = hashlib.sha1()
        hasher.update(msg)
        accept = base64.b64encode(hasher.digest())

        # Successful completion
        response.status = 101
        response.close = False
        try:
            del response.headers["Content-Type"]
        except KeyError:
            pass
        response.headers["Upgrade"] = "WebSocket"
        response.headers["Connection"] = "Upgrade"
        response.headers["Sec-WebSocket-Accept"] = accept
        response.body = ["WebSocket Protocol Handshake"]
        codec = WebSocketCodec(request.sock, channel=self._wschannel)
        self._codecs[request.sock] = codec
        codec.register(self)
        self.fire(connect(request.sock, *request.sock.getpeername()),
                  self._wschannel)
        return response

    @handler("disconnect")
    def _on_disconnect(self, sock):
        if sock in self._codecs:
            del self._codecs[sock]


class WebSockets(object):
    """WebSockets Dispatcher

    .. deprecated:: 2.2
       Use :class:`WebSocketsDispatcher`
    """

    @deprecated
    def __new__(cls, *args, **kwargs):
        return WebSocketsDispatcher(*args, **kwargs)
