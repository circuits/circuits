# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""


from urllib import unquote
from urlparse import urlparse
from traceback import format_exc

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from circuits import handler, Component

import wrappers
from utils import quoted_slash
from headers import parseHeaders
from errors import HTTPError, NotFound
from constants import RESPONSES, BUFFER_SIZE
from events import Request, Response, Stream, Write, Close

class HTTP(Component):
    """HTTP Protocol Component

    Implements the HTTP server protocol and parses and processes incoming
    HTTP messages creating and sending an appropriate response.
    """

    channel = "http"

    def __init__(self, *args, **kwargs):
        super(HTTP, self).__init__(*args, **kwargs)

        self._buffered = {}

    def _handleError(self, error):
        response = error.response

        v = self.send(error, "httperror", self.channel)

        if v:
            if issubclass(type(v), basestring):
                response.body = v
                res = Response(response)
                self.send(res, "response", self.channel)
            elif isinstance(v, HTTPError):
                self.send(Response(v.response), "response", self.channel)
            else:
                assert v, "type(v) == %s" % type(v)

    def stream(self, response):
        data = response.body.read(BUFFER_SIZE)
        if data:
            self.send(Write(response.sock, data), "write", "server")
            self.push(Stream(response))
        else:
            response.body.close()
            if response.close:
                self.send(Close(response.sock), "close", "server")
            response.done = True
        
    def response(self, response):
        self.send(Write(response.sock, str(response)), "write", "server")
        if response.stream:
            self.push(Stream(response), "stream", self.channel)
            return

        if response.close:
            self.send(Close(response.sock), "close", "server")

        response.done = True

    @handler("read", target="server")
    def read(self, sock, data):
        """Read Event Handler

        Process any incoming data appending it to an internal buffer.
        Split the buffer by the standard HTTP delimiter CRLF and create
        Raw Event per line. Any unfinished lines of text, leave in the buffer.
        """

        if sock in self._buffered:
            request, response = self._buffered[sock]
            request.body.write(data)
            contentLength = int(request.headers.get("Content-Length", "0"))
            if not request.body.tell() == contentLength:
                return
        else:
            requestline, data = data.split("\n", 1)
            requestline = requestline.strip()
            method, path, protocol = requestline.split(" ", 2)
            scheme, location, path, params, qs, frag = urlparse(path)

            protocol = tuple(map(int, protocol[5:].split(".")))
            request = wrappers.Request(sock, method, scheme, path, protocol, qs)
            response = wrappers.Response(sock, request)

            if frag:
                error = HTTPError(request, response, 400)
                return self.send(error, "httperror", self.channel)
        
            if params:
                path = "%s;%s" % (path, params)
        
            # Unquote the path+params (e.g. "/this%20path" -> "this path").
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
            #
            # But note that "...a URI must be separated into its components
            # before the escaped characters within those components can be
            # safely decoded." http://www.ietf.org/rfc/rfc2396.txt, sec 2.4.2
            path = "%2F".join(map(unquote, quoted_slash.split(path)))
        
            # Compare request and server HTTP protocol versions, in case our
            # server does not support the requested protocol. Limit our output
            # to min(req, server). We want the following output:
            #    request    server   actual written supported response
            #    protocol protocol response protocol    feature set
            # a  1.0        1.0         1.0             1.0
            # b  1.0        1.1         1.1             1.0
            # c  1.1        1.0         1.0             1.0
            # d  1.1        1.1         1.1             1.1
            # Notice that, in (b), the response will be "HTTP/1.1" even though
            # the client only understands 1.0. RFC 2616 10.5.6 says we should
            # only return 505 if the _major_ version is different.
            if not request.protocol[0] == request.server_protocol[0]:
                error = HTTPError(request, response, 505)
                return self.send(error, "httperror", self.channel)

            headers, body = parseHeaders(StringIO(data))
            request.headers = headers
            request.body.write(body)
            
            if headers.get("Expect", "") == "100-continue":
                self._buffered[sock] = request, response
                return self.simple(sock, 100)

            contentLength = int(headers.get("Content-Length", "0"))
            if not request.body.tell() == contentLength:
                self._buffered[sock] = request, response
                return

        response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

        # Persistent connection support
        if request.protocol == (1, 1):
            # Both server and client are HTTP/1.1
            if request.headers.get("Connection", "") == "close":
                response.close = True
                response.headers.add_header("Connection", "close")
        else:
            # Either the server or client (or both) are HTTP/1.0
            if request.headers.get("Connection", "") != "Keep-Alive":
                response.close = True
                response.headers.add_header("Connection", "close")

        request.body.seek(0)

        try:
            req = Request(request, response)

            v = self.send(req, "request", "web", errors=True)

            if v:
                if issubclass(type(v), basestring):
                    response.body = v
                    res = Response(response)
                    self.send(res, "response", self.channel)
                elif isinstance(v, HTTPError):
                    self._handleError(v)
                elif isinstance(v, wrappers.Response):
                    res = Response(v)
                    self.send(res, "response", self.channel)
                else:
                    assert v, "type(v) == %s" % type(v)
            else:
                error = NotFound(request, response)
                self._handleError(error)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            error = HTTPError(request, response, 500, error=format_exc())
            self._handleError(error)
        finally:
            if sock in self._buffered:
                del self._buffered[sock]

    def simple(self, sock, code, message=""):
        """Simple Response Events Handler

        Send a simple response.
        """

        short, long = RESPONSES.get(code, ("???", "???",))
        message = message or short

        response = wrappers.Response(sock)
        response.body = message
        response.status = "%s %s" % (code, message)

        if response.status[:3] == "413" and response.protocol == "HTTP/1.1":
            # Request Entity Too Large
            response.close = True
            response.headers.add_header("Connection", "close")

        self.send(Response(response), "response", self.channel)

    def httperror(self, request, response, status, message=None, error=None):
        """Default HTTP Error Handler
        
        Default Error Handler that by default just responds with the response
        in the error object passed. The response is normally modified by a
        HTTPError instance or a subclass thereof.
        """

        self.send(Response(response), "response", self.channel)
