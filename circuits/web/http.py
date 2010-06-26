# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""


from urllib import unquote
from urlparse import urlparse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from circuits.net.sockets import Close, Write
from circuits.core import handler, Component, Value

import wrappers
from utils import quoted_slash
from constants import RESPONSES
from headers import parseHeaders
from errors import HTTPError, NotFound
from events import Request, Response, Stream

class HTTP(Component):
    """HTTP Protocol Component

    Implements the HTTP server protocol and parses and processes incoming
    HTTP messages creating and sending an appropriate response.
    """

    def __init__(self, *args, **kwargs):
        super(HTTP, self).__init__(*args, **kwargs)

        self._clients = {}

    def stream(self, response, data):
        if data:
            if response.chunked:
                buf = [hex(len(data))[2:], "\r\n", data, "\r\n"]
                data = "".join(buf)
            self.push(Write(response.sock, data))
            if response.body and not response.done:
                try:
                    data = response.body.next()
                except StopIteration:
                    data = None
                self.push(Stream(response, data))
        else:
            if response.body:
                response.body.close()
            if response.chunked:
                self.push(Write(response.sock, "0\r\n\r\n"))
            if response.close:
                self.push(Close(response.sock))
            response.done = True
        
    def response(self, response):
        self.push(Write(response.sock, str(response)))

        if response.stream and response.body:
            try:
                data = response.body.next()
            except StopIteration:
                data = None
            self.push(Stream(response, data))
        else:
            body = "".join(response.body)

            if body:
                if response.chunked:
                    buf = [hex(len(body))[2:], "\r\n", body, "\r\n"]
                    body = "".join(buf)

                self.push(Write(response.sock, body))

                if response.chunked:
                    self.push(Write(response.sock, "0\r\n\r\n"))

            if not response.stream:
                if response.close:
                    self.push(Close(response.sock))
                response.done = True

    def disconnect(self, sock):
        if sock in self._clients:
            request, response = self._clients[sock]
            del self._clients[sock]

    def read(self, sock, data):
        """Read Event Handler

        Process any incoming data appending it to an internal buffer.
        Split the buffer by the standard HTTP delimiter CRLF and create
        Raw Event per line. Any unfinished lines of text, leave in the buffer.
        """

        if sock in self._clients:
            request, response = self._clients[sock]
            if response.done:
                del self._clients[sock]

        if sock in self._clients:
            request, response = self._clients[sock]
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
            self._clients[sock] = request, response

            if frag:
                error = HTTPError(request, response, 400)
                return self.push(error)
        
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
                return self.push(HTTPError(request, response, 505))

            rp = request.protocol
            sp = request.server_protocol
            response.protocol = "HTTP/%s.%s" % min(rp, sp)

            headers, body = parseHeaders(StringIO(data))
            request.headers = headers
            request.body.write(body)
            
            if headers.get("Expect", "") == "100-continue":
                return self.simple(request, response, 100)

            contentLength = int(headers.get("Content-Length", "0"))
            if not request.body.tell() == contentLength:
                return

        # Persistent connection support
        if request.protocol == (1, 1):
            # Both server and client are HTTP/1.1
            if request.headers.get("Connection", "").lower() == "close":
                response.close = True
        else:
            # Either the server or client (or both) are HTTP/1.0
            if request.headers.get("Connection", "").lower() != "keep-alive":
                response.close = True

        request.body.seek(0)

        self.push(Request(request, response))

    def simple(self, request, response, code, message=""):
        """Simple Response Events Handler

        Send a simple response.
        """

        short, long = RESPONSES.get(code, ("???", "???",))
        message = message or short

        response = wrappers.Response(request.sock, request)
        response.body = message
        response.status = "%s %s" % (code, message)

        if response.status[:3] == "413" and response.protocol == "HTTP/1.1":
            # Request Entity Too Large
            response.close = True
            response.headers.add_header("Connection", "close")

        self.push(Response(response))

    def httperror(self, request, response, status, message=None, error=None):
        """Default HTTP Error Handler
        
        Default Error Handler that by default just responds with the response
        in the error object passed. The response is normally modified by a
        HTTPError instance or a subclass thereof.
        """

        self.push(Response(response))

    def valuechanged(self, value):
        request, response = value.event.args[:2]
        if value.result and not value.errors:
            response.body = value.value
            self.push(Response(response))
        else:
            # This possibly never occurs.
            message = "Request Failed"
            error = value.value
            self.push(HTTPError(request, response, 500, message, error))

    @handler("request_success", "request_filtered")
    def request_success_or_filtered(self, evt, handler, retval):
        if retval:
            request, response = evt.args[:2]
            request.handled = True
            if isinstance(retval, HTTPError):
                self.push(retval, "httperror", self.channel)
            elif isinstance(retval, wrappers.Response):
                self.push(Response(retval))
            elif isinstance(retval, Value):
                if retval.result and not retval.errors:
                    response.body = retval.value
                    self.push(Response(response))
                elif retval.errors:
                    message = "Request Failed"
                    error = retval.value
                    self.push(HTTPError(request, response, 500, message, error))
                else:
                    if retval.manager is None:
                        retval.manager = self
                    retval.event = evt
                    retval.onSet = "valuechanged", self
            elif type(retval) is not bool:
                response.body = retval
                self.push(Response(response))

    def request_failure(self, evt, handler, error):
        request, response = evt.args[:2]
        message = "Request Failed"
        self.push(HTTPError(request, response, 500, message, error))

    def request_completed(self, evt, handler, retval):
        request, response = evt.args[:2]
        if not request.handled or handler is None:
            self.push(NotFound(request, response), "httperror", self.channel)
