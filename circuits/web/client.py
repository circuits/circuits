
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from circuits.web.headers import Headers
from circuits.core import handler, BaseComponent, Event
from circuits.net.sockets import TCPClient, Connect, Write, Close

from circuits.net.protocols.http import HTTP


def parse_url(url):
    p = urlparse(url)

    if p.hostname:
        host = p.hostname
    else:
        raise ValueError("URL must be absolute")

    if p.scheme == "http":
        secure = False
        port = p.port or 80
    elif p.scheme == "https":
        secure = True
        port = p.port or 443
    else:
        raise ValueError("Invalid URL scheme")

    resource = p.path or "/"

    if p.query:
        resource += "?" + p.query

    return (host, port, resource, secure)


class HTTPException(Exception):
    pass


class NotConnected(HTTPException):
    pass


class Request(Event):
    """Request Event

    This Event is used to initiate a new request.

    :param method: HTTP Method (PUT, GET, POST, DELETE)
    :type  method: str

    :param path: Path to resource
    :type  path: str
    """

    def __init__(self, method, path, body=None, headers={}):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Request, self).__init__(method, path, body, headers)


class Client(BaseComponent):

    channel = "client"

    def __init__(self, url, channel=channel):
        super(Client, self).__init__(channel=channel)
        self._host, self._port, self._resource, self._secure = parse_url(url)

        self._response = None

        self._transport = TCPClient(channel=channel).register(self)

        HTTP(channel=channel).register(self._transport)

    @handler("write")
    def write(self, data):
        if self._transport.connected:
            self.fire(Write(data), self._transport)

    @handler("close")
    def close(self):
        if self._transport.connected:
            self.fire(Close(), self._transport)

    @handler("connect")
    def connect(self):
        if not self._transport.connected:
            self.fire(Connect(self._host, self._port, self._secure),
                    self._transport)

    @handler("request")
    def request(self, method, path, body=None, headers={}):
        if self._transport.connected:
            headers = Headers([(k, v) for k, v in headers.items()])
            # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
            if not headers.has_key("Host"):
                headers["Host"] = self._host \
                    + (":" + str(self._port)) if self._port else ""
            command = "%s %s HTTP/1.1" % (method, path)
            message = "%s\r\n%s" % (command, headers)
            self.fire(Write(message.encode('utf-8')), self._transport)
            if body:
                self.fire(Write(body), self._transport)
        else:
            raise NotConnected()

    @handler("response")
    def _on_response(self, response):
        self._response = response
        if response.headers.get("Connection") == "Close":
            self.fire(Close(), self._transport)

    @property
    def connected(self):
        if hasattr(self, "_transport"):
            return self._transport.connected

    @property
    def response(self):
        return getattr(self, "_response", None)
