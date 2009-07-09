# Module:   wrappers
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Request/Response Wrappers

This module implements the Request and Response objects.
"""


import os
import stat
import types
from cStringIO import StringIO
from time import strftime, time
from Cookie import SimpleCookie

from headers import Headers
from constants import BUFFER_SIZE, SERVER_VERSION

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

class Request(object):
    """Creates a new Request object to hold information about a request.
    
    @param sock: The socket object of the request.
    @type  sock: socket.socket

    @param method: The requsted method.
    @type  method: str

    @param scheme: The requsted scheme.
    @type  scheme: str

    @param path: The requsted path.
    @type  path: str

    @param protocol: The requsted protocol.
    @type  protocol: str

    @param qs: The query string of the request.
    @type  qs: str
    """

    server = None
    """@cvar: A reference to the underlying server"""

    scheme = "http"
    protocol = (1, 1)
    server_protocol = (1, 1)
    host = ""
    local = Host("127.0.0.1", 80)
    remote = Host("127.0.0.1", 1111)

    index = None
    script_name = ""

    login = None
    handled = False

    def __init__(self, sock, method, scheme, path, protocol, qs):
        "initializes x; see x.__class__.__doc__ for signature"

        self.sock = sock
        self.method = method
        self.scheme = scheme or Request.scheme
        self.path = path
        self.protocol = protocol
        self.qs = qs
        self.cookie = SimpleCookie()

        self._headers = None

        if sock:
            self.remote = Host(*sock.getpeername())

        self.body = StringIO()

    def _getHeaders(self):
        return self._headers

    def _setHeaders(self, headers):
        self._headers = headers

        if "Cookie" in self.headers:
            self.cookie.load(self.headers["Cookie"])

        host = self.headers.get("Host", None)
        if not host:
            host = self.local.name or self.local.ip
        self.base = "%s://%s" % (self.scheme, host)

    headers = property(_getHeaders, _setHeaders)

    def __repr__(self):
        protocol = "HTTP/%d.%d" % self.protocol
        return "<Request %s %s %s>" % (self.method, self.path, protocol)

class Response(object):
    """Response(sock, request) -> new Response object

    A Response object that holds the response to
    send back to the client. This ensure that the correct data
    is sent in the correct order.
    """

    chunked = False

    def __init__(self, sock, request):
        "initializes x; see x.__class__.__doc__ for signature"

        self.sock = sock
        self.request = request
        self.clear()

    def __repr__(self):
        return "<Response %s %s (%d)>" % (
                self.status,
                self.headers["Content-Type"],
                (len(self.body) if type(self.body) == str else 0))
    
    def output(self):
        protocol = "HTTP/%d.%d" % self.request.server_protocol
        status = self.status
        headers = self.headers
        body = self.process() or ""
        yield "%s %s\r\n" % (protocol, status)
        yield str(headers)
        if body:
            if self.chunked:
                buf = [hex(len(body))[2:], "\r\n", body, "\r\n"]
                yield "".join(buf)
            else:
                yield body

    def clear(self):
        self.done = False
        self.close = False
        
        if self.request.server:
            server_version = self.request.server.version
        else:
            server_version = SERVER_VERSION

        self.headers = Headers([
            ("Server", server_version),
            ("Date", strftime("%a, %d %b %Y %H:%M:%S %Z")),
            ("X-Powered-By", server_version)])

        self.cookie = self.request.cookie

        self.stream = False
        self.body = None
        self.time = time()
        self.status = "200 OK"

    def process(self):
        for k, v in self.cookie.iteritems():
            self.headers.add_header("Set-Cookie", v.OutputString())

        status = int(self.status.split(" ", 1)[0])

        if status == 413:
            self.close = True
        elif "Content-Length" not in self.headers:
            if status < 200 or status in (204, 205, 304):
                pass
            else:
                if self.protocol == "HTTP/1.1" \
                        and self.request.method != "HEAD":
                    self.chunked = True
                    self.headers.add_header("Transfer-Encoding", "chunked")
                else:
                    self.close = True

        if "Connection" not in self.headers:
            if self.protocol == "HTTP/1.1":
                if self.close:
                    self.headers.add_header("Connection", "close")
            else:
                if not self.close:
                    self.headers.add_header("Connection", "Keep-Alive")

        if type(self.body) is types.FileType:
            cType = self.headers.get("Content-Type", "application/octet-stream")
            cLen = os.fstat(self.body.fileno())[stat.ST_SIZE]

            if cLen > BUFFER_SIZE:
                body = self.body.read(BUFFER_SIZE)
                self.stream = True
            else:
                body = self.body.read()
        elif issubclass(type(self.body), basestring):
            body = self.body
            cLen = len(body)
            cType = self.headers.get("Content-Type", "text/html")
        elif type(self.body) is types.GeneratorType:
            self.stream = True
            return self.body.next()
        else:
            return None

        self.headers["Content-Type"] = cType
        self.headers["Content-Length"] = str(cLen)

        return body
