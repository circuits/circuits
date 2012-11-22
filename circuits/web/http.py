# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""


from io import BytesIO
try:
    from urllib.parse import unquote
    from urllib.parse import urlparse
except ImportError:
    from urllib import unquote
    from urlparse import urlparse

from circuits.net.sockets import Close, Write
from circuits.core import handler, BaseComponent, Value

from . import wrappers
from .utils import quoted_slash
from .exceptions import HTTPException
from .headers import parse_headers, Headers
from .events import Request, Response, Stream
from .errors import HTTPError, NotFound, Redirect
from .exceptions import Redirect as RedirectException

MAX_HEADER_FRAGENTS = 20
HTTP_ENCODING = 'utf-8'

try:
    unicode
except NameError:
    unicode = str


class HTTP(BaseComponent):
    """HTTP Protocol Component

    Implements the HTTP server protocol and parses and processes incoming
    HTTP messages creating and sending an appropriate response.
    """

    channel = "web"

    def __init__(self, encoding="utf-8", channel=channel):
        super(HTTP, self).__init__(channel=channel)

        self._encoding = encoding

        self._clients = {}
        self._buffers = {}

    @handler("stream")
    def _on_stream(self, response, data):
        if data is not None:
            if data:
                if response.chunked:
                    buf = [hex(len(data))[2:], b"\r\n", data, b"\r\n"]
                    data = b"".join(buf)
                self.fire(Write(response.request.sock, data))
            if response.body and not response.done:
                try:
                    data = next(response.body)
                except StopIteration:
                    data = None
                self.fire(Stream(response, data))
        else:
            if response.body:
                response.body.close()
            if response.chunked:
                self.fire(Write(response.request.sock, b"0\r\n\r\n"))
            if response.close:
                self.fire(Close(response.request.sock))
            response.done = True

    @handler("response")
    def _on_response(self, response):
        self.fire(
                Write(response.request.sock,
                    str(response).encode(HTTP_ENCODING)))

        if response.stream and response.body:
            try:
                data = next(response.body)
            except StopIteration:
                data = None
            self.fire(Stream(response, data))
        else:
            if isinstance(response.body, bytes):
                body = response.body
            elif isinstance(response.body, unicode):
                body = response.body.encode(self._encoding)
            else:
                parts = (s if isinstance(s, bytes) else s.encode(self._encoding) \
                    for s in response.body if s is not None)
                body = b"".join(parts)

            if body:
                if response.chunked:
                    buf = [hex(len(body))[2:].encode(), b"\r\n", body, b"\r\n"]
                    body = b"".join(buf)
                self.fire(Write(response.request.sock, body))

                if response.chunked:
                    self.fire(Write(response.request.sock, b"0\r\n\r\n"))

            if not response.stream:
                if response.close:
                    self.fire(Close(response.request.sock))
                response.done = True

    @handler("disconnect")
    def _on_disconnect(self, sock):
        if sock in self._clients:
            del self._clients[sock]

    @handler("read")
    def _on_read(self, sock, data):
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
            if data.find(b'\r\n\r\n') == -1:
                buf = self._buffers.setdefault(sock, [])
                buf.append(data)
                if len(buf) > MAX_HEADER_FRAGENTS:
                    del self._buffers[sock]
                    raise ValueError("Too many HTTP Headers Fragments.")
                return
            if sock in self._buffers:
                self._buffers[sock].append(data)
                data = ''.join(self._buffers[sock])
                del self._buffers[sock]

            requestline, data = data.split(b"\r\n", 1)
            requestline = requestline.strip().decode(
                    HTTP_ENCODING, "replace")
            method, path, protocol = requestline.split(" ", 2)
            scheme, location, path, params, qs, frag = urlparse(path)

            protocol = tuple(map(int, protocol[5:].split(".")))
            request = wrappers.Request(sock, method, scheme, path,
                    protocol, qs)
            response = wrappers.Response(request, encoding=self._encoding)
            self._clients[sock] = request, response

            if frag:
                return self.fire(HTTPError(request, response, 400))

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
                return self.fire(HTTPError(request, response, 505))

            rp = request.protocol
            sp = request.server_protocol
            response.protocol = "HTTP/%s.%s" % min(rp, sp)

            end_of_headers = data.find(b"\r\n\r\n")
            if end_of_headers > -1:
                header_data = data[:end_of_headers].decode(
                        HTTP_ENCODING, "replace")
                headers = request.headers = parse_headers(header_data)
            else:
                headers = request.headers = Headers([])

            request.body.write(data[(end_of_headers + 4):])

            if headers.get("Expect", "") == "100-continue":
                return self.fire(Response(wrappers.Response(request, code=100,
                    encoding=self._encoding)))

            contentLength = int(headers.get("Content-Length", "0"))
            if request.body.tell() < contentLength:
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

        if hasattr(sock, "getpeercert"):
            peer_cert = sock.getpeercert()
            if peer_cert:
                req = Request(request, response, peer_cert)
            else:
                req = Request(request, response)
        else:
            req = Request(request, response)

        self.fire(req)

    @handler("httperror")
    def _on_httperror(self, event, request, response, code, **kwargs):
        """Default HTTP Error Handler

        Default Error Handler that by default just responds with the response
        in the error object passed. The response is normally modified by a
        HTTPError instance or a subclass thereof.
        """

        response.body = str(event)
        self.fire(Response(response))

    @handler("request_value_changed")
    def _on_request_value_changed(self, value):
        if value.handled:
            return
        request, response = value.event.args[:2]
        if value.result and not value.errors:
            response.body = value.value
            self.fire(Response(response))
        else:
            # This possibly never occurs.
            self.fire(HTTPError(request, response, error=value.value))

    @handler("request_success")
    def _on_request_success(self, e, value):
        # We only want the non-recursive value at this point.
        # If the value is an instance of Value we will set
        # the .notify flag and be notified of changes to the value.
        value = e.value.getValue(recursive=False)

        if isinstance(value, Value) and not value.promise:
            value = value.getValue(recursive=False)

        request, response = e.args[:2]

        if value is None:
            self.fire(NotFound(request, response))
        elif isinstance(value, HTTPError):
            response.body = str(value)
            self.fire(Response(response))
        elif isinstance(value, wrappers.Response):
            self.fire(Response(value))
        elif isinstance(value, Value):
            if value.result and not value.errors:
                response.body = value.value
                self.fire(Response(response))
            elif value.errors:
                error = value.value
                etype, evalue, traceback = error
                if isinstance(evalue, RedirectException):
                    self.fire(Redirect(request, response,
                        evalue.urls, evalue.status))
                elif isinstance(evalue, HTTPException):
                    if evalue.traceback:
                        self.fire(HTTPError(request, response, evalue.code,
                            description=evalue.description, error=error))
                    else:
                        self.fire(HTTPError(request, response, evalue.code,
                            description=evalue.description))
                else:
                    self.fire(HTTPError(request, response, error=error))
            else:
                # We want to be notified of changes to the value
                value = e.value.getValue(recursive=False)
                value.event = e
                value.notify = True
        elif type(value) is tuple:
            etype, evalue, traceback = error = value

            if isinstance(evalue, RedirectException):
                self.fire(Redirect(request, response,
                    evalue.urls, evalue.status))
            elif isinstance(evalue, HTTPException):
                if evalue.traceback:
                    self.fire(HTTPError(request, response, evalue.code,
                        description=evalue.description, error=error))
                else:
                    self.fire(HTTPError(request, response, evalue.code,
                        description=evalue.description))
            else:
                self.fire(HTTPError(request, response, error=error))
        elif type(value) is not bool:
            response.body = value
            self.fire(Response(response))

    @handler("request_failure", "response_failure")
    def _on_request_or_response_failure(self, evt, err):
        if len(evt.args) == 1:
            response = evt.args[0]
            request = response.request
        else:
            request, response = evt.args[:2]

        # Ignore filtered requests already handled (eg: HTTPException(s)).
        # Ignore failed "response" handlers (eg: Loggers or Tools)
        if request.handled or response.done:
            return

        if not request.handled:
            request.handled = True

        etype, evalue, traceback = err

        if isinstance(evalue, RedirectException):
            self.fire(Redirect(request, response,
                evalue.urls, evalue.status))
        elif isinstance(evalue, HTTPException):
            if evalue.traceback:
                self.fire(HTTPError(request, response, evalue.code,
                    description=evalue.description, error=err))
            else:
                self.fire(HTTPError(request, response, evalue.code,
                    description=evalue.description))
        else:
            self.fire(HTTPError(request, response, error=err))
