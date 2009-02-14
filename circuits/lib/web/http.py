# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""

from re import split
from cgi import escape
from urllib import unquote
from urlparse import urlparse
from cStringIO import StringIO
from traceback import format_exc

import circuits
from circuits.core import listener, Component

import webob
from headers import parseHeaders
from utils import quoted_slash, quoteHTML
from constants import DEFAULT_ERROR_MESSAGE, RESPONSES
from constants import BUFFER_SIZE, SERVER_PROTOCOL, SERVER_VERSION
from events import Request, Response, Stream, Write, HTTPError, Close

class HTTP(Component):
    """HTTP() -> HTTP Component

    Create a new HTTP object which implements the HTTP
    protocol. Note this doesn"t actually do anything
    usefull unless used in conjunction with either:
     * circuits.parts.sockets.TCPClient or
     * circuits.parts.sockets.TCPServer

    Sub-classes that wish to do something usefull with
    events that are processed and generated, must have
    filters/listeners associated with them. For instance,
    to do something with ... events:

    {{{
    #!python
    class Client(HTTP):

        @listener("...")
        def on...(self, ...):
            ...
    }}}

    The available events that are processed and generated
    are pushed onto channels associated with that event.
    They are:
     * ...
    """

    _requests = {}

    def __init__(self, server, *args, **kwargs):
        super(HTTP, self).__init__(*args, **kwargs)

        self.server = server

    def stream(self, response):
        data = response.body.read(BUFFER_SIZE)
        if data:
            self.send(Write(response.sock, data), "write")
            self.push(Stream(response), "stream")
        else:
            response.body.close()
            if response.close:
                self.send(Close(response.sock), "close")
        
    def response(self, response):
        self.send(Write(response.sock, str(response)), "write")
        if response.stream:
            self.push(Stream(response), "stream")
        elif response.close:
            self.send(Close(response.sock), "close")

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
            requestline, data = split("\r?\n", data, 1)
            method, path, protocol = requestline.strip().split(" ", 2)
            scheme, location, path, params, qs, frag = urlparse(path)

            request = webob.Request(method, path, protocol, qs)
            request.server = self.server
            response = webob.Response(sock)

            request.scheme = scheme
            request.server_protocol = protocol
            request.request_line = requestline

            if frag:
                error = HTTPError(request, response, 400)
                return self.send(error, "httperror")
        
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
            rp = int(protocol[5]), int(protocol[7])
            sp = int(SERVER_PROTOCOL[5]), int(SERVER_PROTOCOL[7])
            if sp[0] != rp[0]:
                error = HTTPError(request, response, 505)
                return self.send(error, "httperror")

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
        if request.protocol == "HTTP/1.1":
            # Both server and client are HTTP/1.1
            if request.headers.get("HTTP_CONNECTION", "") == "close":
                response.close = True
        else:
            # Either the server or client (or both) are HTTP/1.0
            if request.headers.get("HTTP_CONNECTION", "") != "Keep-Alive":
                response.close = True

        request.body.seek(0)

        try:
            req = Request(request, response)
            v = [x for x in self.iter(req, "request") if x]

            if v:
                if isinstance(v[0], basestring):
                    response.body = v[0]
                res = Response(response)
                self.send(res, "response")
            else:
                error = HTTPError(request, response, 404)
                self.send(error, "httperror")
        except Exception, error:
            error = HTTPError(request, response, 500, error=format_exc())
            self.send(error, "httperror")
        finally:
            if sock in self._requests:
                del self._requests[sock]

    ###
    ### Supporting Functions
    ###

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

        self.send(Response(response), "response")

    def httperror(self, request, response, status, message=None, error=None):
        """HTTP Error Event Handler
        
        Arguments are the error code status, and a detailed message.
        The detailed message defaults to the short entry matching the
        response status.

        This sends an error response (so it must be called before any
        output has been generated), and sends a piece of HTML explaining
        the error to the user.
        """

        short, long = RESPONSES.get(status, ("???", "???",))
        message = message or short

        s = DEFAULT_ERROR_MESSAGE % {
            "status": "%s %s" % (status, short),
            "message": escape(message),
            "traceback": error or "",
            "version": SERVER_VERSION}

        response.clear()
        response.body = s
        response.status = "%s %s" % (status, message)
        response.headers.add_header("Connection", "close")

        self.send(Response(response), "response")
