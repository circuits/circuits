# Module:   websockets
# Date:     26th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au
from circuits.web.errors import HTTPError
from circuits.net.protocols.websocket import WebSocketCodec

import hashlib
import base64
from circuits.core.handlers import handler

from circuits import BaseComponent
from circuits.net.sockets import Connect


class WebSockets(BaseComponent):
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
    the constructor. The data from :class:`~.sockets.Write` events on 
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
            
        :param wschannel: the channel on which :class:`~.sockets.Read`
            events from the client will be delivered and where
            :class:`~.sockets.Write` events to the client will be
            sent to.
        """
        super(WebSockets, self).__init__(*args, **kwargs)

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
        self.fire(Connect(request.sock, *request.sock.getpeername()),
                  self._wschannel)
        return response
        
    @handler("disconnect")
    def _on_disconnect(self, sock):
        if self._codecs.has_key(sock):
            del self._codecs[sock]

