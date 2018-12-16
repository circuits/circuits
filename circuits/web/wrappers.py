"""Request/Response Wrappers

This module implements the Request and Response objects.
"""
from functools import partial
from io import BytesIO
from time import time

from circuits.net.sockets import BUFSIZE
from circuits.six import binary_type, text_type

from .constants import HTTP_STATUS_CODES, SERVER_VERSION
from .errors import httperror
from .headers import Headers
from .url import parse_url

try:
    from Cookie import SimpleCookie
except ImportError:
    from http.cookies import SimpleCookie  # NOQA

try:
    from email.utils import formatdate
    formatdate = partial(formatdate, usegmt=True)
except ImportError:
    from rfc822 import formatdate  # NOQA


try:
    unicode
except NameError:
    unicode = str


def file_generator(input, chunkSize=BUFSIZE):
    chunk = input.read(chunkSize)
    while chunk:
        yield chunk
        chunk = input.read(chunkSize)
    input.close()


class Host(object):

    """An internet address.

    name should be the client's host name. If not available (because no DNS
    lookup is performed), the IP address should be used instead.
    """

    ip = "0.0.0.0"
    port = 80
    name = "unknown.tld"

    def __init__(self, ip, port, name=None):
        self.ip = ip
        self.port = port
        if name is None:
            name = ip
        self.name = name

    def __repr__(self):
        return "Host(%r, %r, %r)" % (self.ip, self.port, self.name)


class HTTPStatus(object):

    __slots__ = ("_reason", "_status",)

    def __init__(self, status=200, reason=None):
        self._status = status
        self._reason = reason or HTTP_STATUS_CODES.get(status, "")

    def __int__(self):
        return self._status

    def __lt__(self, other):
        if isinstance(other, int):
            return self._status < other
        return super(HTTPStatus, self).__lt__(other)

    def __gt__(self, other):
        if isinstance(other, int):
            return self._status > other
        return super(HTTPStatus, self).__gt__(other)

    def __le__(self, other):
        if isinstance(other, int):
            return self._status <= other
        return super(HTTPStatus, self).__le__(other)

    def __ge__(self, other):
        if isinstance(other, int):
            return self._status >= other
        return super(HTTPStatus, self).__ge__(other)

    def __eq__(self, other):
        if isinstance(other, int):
            return self._status == other
        return super(HTTPStatus, self).__eq__(other)

    def __str__(self):
        return "{0:d} {1:s}".format(self._status, self._reason)

    def __repr__(self):
        return "<Status (status={0:d} reason={1:s}>".format(
            self._status, self._reason
        )

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    @property
    def status(self):
        return self._status

    @property
    def reason(self):
        return self._reason


class Request(object):

    """Creates a new Request object to hold information about a request.

    :param sock: The socket object of the request.
    :type  sock: socket.socket

    :param method: The requested method.
    :type  method: str

    :param scheme: The requested scheme.
    :type  scheme: str

    :param path: The requested path.
    :type  path: str

    :param protocol: The requested protocol.
    :type  protocol: str

    :param qs: The query string of the request.
    :type  qs: str
    """

    server = None
    """:cvar: A reference to the underlying server"""

    scheme = "http"
    protocol = (1, 1)
    host = ""
    local = Host("127.0.0.1", 80)
    remote = Host("", 0)

    index = None
    script_name = ""

    login = None
    handled = False

    def __init__(self, sock, method="GET", scheme="http", path="/",
                 protocol=(1, 1), qs="", headers=None, server=None):
        "initializes x; see x.__class__.__doc__ for signature"

        self.sock = sock
        self.method = method
        self.scheme = scheme or Request.scheme
        self.path = path
        self.protocol = protocol
        self.qs = qs
        self.print_debug = getattr(server, "display_banner", False)

        self.headers = headers or Headers()
        self.server = server

        self.cookie = SimpleCookie()

        if sock is not None:
            name = sock.getpeername()
            try:
                ip, port = name
                name = None
            except ValueError:  # AF_UNIX
                ip, port = None, None
            self.remote = Host(ip, port, name)

        cookie = self.headers.get("Cookie")
        if cookie is not None:
            self.cookie.load(cookie)

        self.body = BytesIO()

        if self.server is not None:
            self.local = Host(self.server.host, self.server.port)

        try:
            host = self.headers["Host"]
            if ":" in host:
                parts = host.split(":", 1)
                host = parts[0]
                port = int(parts[1])
            else:
                port = 443 if self.scheme == "https" else 80
        except KeyError:
            host = self.local.name or self.local.ip
            port = getattr(self.server, "port")

        self.host = host
        self.port = port

        base = "{0:s}://{1:s}{2:s}/".format(
            self.scheme,
            self.host,
            ":{0:d}".format(self.port)
            if self.port not in (80, 443)
            else ""
        )

        self.base = parse_url(base)

        url = "{0:s}{1:s}{2:s}".format(
            base,
            self.path,
            "?{0:s}".format(self.qs) if self.qs else ""
        )
        self.uri = parse_url(url)
        self.uri.sanitize()

    def __repr__(self):
        protocol = "HTTP/%d.%d" % self.protocol
        return "<Request %s %s %s>" % (self.method, self.path, protocol)


class Body(object):

    """Response Body"""

    encode_errors = 'strict'

    def __get__(self, response, cls=None):
        if response is None:
            return self
        else:
            return response._body

    def __set__(self, response, value):
        if response == value:
            return

        if isinstance(value, binary_type):
            if value:
                value = [value]
            else:
                value = []
        elif isinstance(value, text_type):
            if value:
                value = [value.encode(response.encoding, self.encode_errors)]
            else:
                value = []
        elif hasattr(value, "read"):
            response.stream = True
            value = file_generator(value)
        elif isinstance(value, httperror):
            value = [str(value)]
        elif value is None:
            value = []

        response._body = value


class Status(object):

    """Response Status"""

    def __get__(self, response, cls=None):
        if response is None:
            return self
        else:
            return response._status

    def __set__(self, response, value):
        value = HTTPStatus(value) if isinstance(value, int) else value

        response._status = value


class Response(object):

    """Response(sock, request) -> new Response object

    A Response object that holds the response to
    send back to the client. This ensure that the correct data
    is sent in the correct order.
    """

    body = Body()
    status = Status()

    done = False
    close = False
    stream = False
    chunked = False

    def __init__(self, request, encoding='utf-8', status=None):
        "initializes x; see x.__class__.__doc__ for signature"

        self.request = request
        self.encoding = encoding

        self._body = []
        self._status = HTTPStatus(status if status is not None else 200)

        self.time = time()

        self.headers = Headers()
        self.headers["Date"] = formatdate()

        if getattr(self.request.server, "display_banner", False):
            if self.request.server is not None:
                self.headers.add_header("Server", request.server.http.version)
            else:
                self.headers.add_header("X-Powered-By", SERVER_VERSION)

        self.cookie = self.request.cookie

        self.protocol = "HTTP/%d.%d" % self.request.protocol

    def __repr__(self):
        return "<Response %s %s (%d)>" % (
            self.status,
            self.headers.get("Content-Type"),
            (len(self.body) if isinstance(self.body, str) else 0)
        )

    def __str__(self):
        self.prepare()
        protocol = self.protocol
        status = "{0:s}".format(self.status)
        return "{0:s} {1:s}\r\n".format(protocol, status)

    def __bytes__(self):
        return str(self).encode(self.encoding)  # FIXME: this is wrong. HTTP headers must be ISO8859-1. This should only encode the body as UTF-8.

    def prepare(self):
        # Set a default content-Type if we don't have one.
        self.headers.setdefault(
            "Content-Type", "text/html; charset={0:s}".format(self.encoding)
        )

        cLength = None
        if self.body is not None:
            if isinstance(self.body, bytes):
                cLength = len(self.body)
            elif isinstance(self.body, unicode):
                cLength = len(self.body.encode(self.encoding))
            elif isinstance(self.body, list):
                cLength = sum(
                    [
                        len(s.encode(self.encoding))
                        if not isinstance(s, bytes)
                        else len(s) for s in self.body
                        if s is not None
                    ]
                )

        if cLength is not None:
            self.headers["Content-Length"] = str(cLength)

        for k, v in self.cookie.items():
            self.headers.add_header("Set-Cookie", v.OutputString())

        status = self.status

        if status == 413:
            self.close = True
        elif "Content-Length" not in self.headers:
            if status < 200 or status in (204, 205, 304):
                pass
            else:
                if self.protocol == "HTTP/1.1" \
                        and self.request.method != "HEAD" \
                        and self.request.server is not None \
                        and not cLength == 0:
                    self.chunked = True
                    self.headers.add_header("Transfer-Encoding", "chunked")
                else:
                    self.close = True

        if (self.request.server is not None and "Connection" not in self.headers):
            if self.protocol == "HTTP/1.1":
                if self.close:
                    self.headers.add_header("Connection", "close")
            else:
                if not self.close:
                    self.headers.add_header("Connection", "Keep-Alive")

        if self.headers.get("Transfer-Encoding", "") == "chunked":
            self.chunked = True
