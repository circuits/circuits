# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""

from urllib import unquote
from urlparse import urlparse
from cStringIO import StringIO
from traceback import format_exc

from circuits.core import Component

import webob
from utils import quoted_slash
from headers import parseHeaders
from errors import HTTPError, NotFound
from events import Request, Response, Stream, Write, Close
from constants import RESPONSES, BUFFER_SIZE, SERVER_PROTOCOL

class HTTP(Component):
    """HTTP Protocol Component

    Implements the HTTP server protocol and parses and processes incoming
    HTTP messages then creates and sends appropiate responses.
    """

    _requests = {}

    def __init__(self, server, *args, **kwargs):
        super(HTTP, self).__init__(*args, **kwargs)

        self.server = server

    def _handleError(self, error):
        response = error.response

        try:
            v = self.send(error, "httperror", self.channel)
        except TypeError:
            v = None

        if v is not None:
            if isinstance(v, basestring):
                response.body = v
                res = Response(response)
                self.send(res, "response", self.channel)
            elif isinstance(v, HTTPError):
                self.send(Response(v.response), "response", self.channel)
            else:
                raise TypeError("wtf is %s (%s) response ?!" % (v, type(v)))

    def stream(self, response):
        data = response.body.read(BUFFER_SIZE)
        if data:
            self.send(Write(response.sock, data), "write", self.channel)
            self.push(Stream(response), "stream", self.channel)
        else:
            response.body.close()
            if response.close:
                self.send(Close(response.sock), "close", self.channel)
            response.done = True
        
    def response(self, response):
        self.send(Write(response.sock, str(response)), "write", self.channel)
        if response.stream:
            self.push(Stream(response), "stream", self.channel)
            return
        elif response.close:
            self.send(Close(response.sock), "close", self.channel)

        response.done = True

    def read(self, sock, data):
        """H.read(sock, data) -> None

        Process any incoming data appending it to an internal
        buffer. Split the buffer by the standard HTTP delimiter
        \r\n and create a RawEvent per line. Any unfinished
        lines of text, leave in the buffer.
        """

        if sock in self._requests:
            request = self._requests[sock]
            request.body.write(data)
            contentLength = int(request.headers.get("Content-Length", "0"))
            if not request.body.tell() == contentLength:
                return
        else:
            requestline, data = data.split("\n", 1)
            requestline = requestline.strip()
            method, path, protocol = requestline.split(" ", 2)
            scheme, location, path, params, qs, frag = urlparse(path)

            protocol = tuple([int(x) for x in protocol.split("/")[1].split(".")])
            request = webob.Request(method, path, protocol, qs)
            request.server = self.server
            request.local_host = webob.Host(
                    self.server.address, self.server.port)
            request.remtoe_host = webob.Host(*sock.getpeername())

            response = webob.Response(sock)
            response.request = request

            request.scheme = scheme
            request.server_protocol = SERVER_PROTOCOL
            request.request_line = requestline

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
            atoms = [unquote(x) for x in quoted_slash.split(path)]
            path = "%2F".join(atoms)
        
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
            rp = request.protocol
            sp = request.server_protocol
            if sp[0] != rp[0]:
                error = HTTPError(request, response, 505)
                return self.send(error, "httperror", self.channel)

            headers, body = parseHeaders(StringIO(data))
            request.headers = headers
            request.body.write(body)

            if headers.get("Expect", "") == "100-continue":
                self._requests[sock] = request
                return self.simple(sock, 100)

            contentLength = int(headers.get("Content-Length", "0"))
            if not request.body.tell() == contentLength:
                self._requests[sock] = request
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

            try:
                v = self.send(req, "request", self.channel, errors=True)
            except TypeError:
                v = None

            if v is not None:
                if isinstance(v, basestring):
                    response.body = v
                    res = Response(response)
                    self.send(res, "response", self.channel)
                elif isinstance(v, HTTPError):
                    self._handleError(v)
                else:
                    raise TypeError("wtf is %s (%s) response ?!" % (v, type(v)))
            else:
                error = NotFound(request, response)
                self._handleError(error)
        except:
            error = HTTPError(request, response, 500, error=format_exc())
            self._handleError(error)
        finally:
            if sock in self._requests:
                del self._requests[sock]

    def simple(self, sock, code, message=""):
        """Simple Response Events Handler

        Send a simple response.
        """

        short, long = RESPONSES.get(code, ("???", "???",))
        message = message or short

        response = webob.Response(sock)
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
