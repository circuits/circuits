
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

    resource = p.path or u"/"

    if p.query:
        resource += u"?" + p.query

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

    def __init__(self, method, path):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Request, self).__init__(method, path)

class Client(BaseComponent):

    channel = "web"

    def __init__(self, url, channel=channel):
        super(Client, self).__init__(channel=channel)

        self._host, self._port, self._resource, self._secure = parse_url(url)

        self._response = None

        self._transport = TCPClient().register(self)

        HTTP().register(self._transport)

    @handler("close")
    def close(self):
        if self._transport.connected:
            self.push(Close(), target=self._transport)

    @handler("connect")
    def connect(self):
        if not self._transport.connected:
            self.push(Connect(self._host, self._port, self._secure),
                    target=self._transport)

    @handler("request")
    def request(self, method, path, body=None, headers={}):
        if self._transport.connected:
            headers = Headers([(k, v) for k, v in headers.items()])
            command = "%s %s HTTP/1.1" % (method, path)
            message = "%s\r\n%s" % (command, headers)
            self.push(Write(message), target=self._transport)
            if body:
                self.push(Write(body), target=self._transport)
        else:
            raise NotConnected()

    @handler("response")
    def _on_response(self, response):
        self._response = response
        if not response.status == 100:
            self.push(Close(), target=self._transport)

    @property
    def connected(self):
        if hasattr(self, "_transport"):
            return self._transport.connected

    @property
    def response(self):
        return getattr(self, "_response", None)
