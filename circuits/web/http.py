# Module:   http
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the server side Hyper Text Transfer Protocol
or commonly known as HTTP.
"""


from io import BytesIO
from posixpath import realpath

try:
    from urllib.parse import unquote
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urllib import unquote  # NOQA
    from urlparse import urlparse, urlunparse  # NOQA


from circuits.net.sockets import Close, Write
from circuits.core import handler, BaseComponent, Value
from circuits.six import b

from . import wrappers
from .utils import is_ssl_handshake
from .exceptions import HTTPException
from .events import Request, Response, Stream
from .parsers import HttpParser, BAD_FIRST_LINE
from .errors import HTTPError, NotFound, Redirect
from .exceptions import Redirect as RedirectException
from .constants import SERVER_VERSION, SERVER_PROTOCOL

MAX_HEADER_FRAGENTS = 20
HTTP_ENCODING = 'utf-8'

try:
    unicode
except NameError:
    unicode = str


class HTTP(BaseComponent):
    """HTTP Protocol Component

    Implements the HTTP server protocol and parses and processes incoming
    HTTP messages, creating and sending an appropriate response.

    The component handles :class:`~circuits.net.sockets.Read` events
    on its channel and collects the associated data until a complete
    HTTP request has been received. It parses the request's content
    and puts it in a :class:`~circuits.web.wrappers.Request` object and
    creates a corresponding :class:`~circuits.web.wrappers.Response`
    object. Then it emits a :class:`~circuits.web.events.Request`
    event with these objects as arguments.

    The component defines several handlers that send a response back to
    the client.
    """

    channel = "web"

    def __init__(self, server, encoding=HTTP_ENCODING, channel=channel):
        super(HTTP, self).__init__(channel=channel)

        self._server = server
        self._encoding = encoding

        self._clients = {}
        self._buffers = {}

    @property
    def version(self):
        return SERVER_VERSION

    @property
    def protocol(self):
        return SERVER_PROTOCOL

    @property
    def scheme(self):
        if not hasattr(self, "_server"):
            return
        return "https" if self._server.secure else "http"

    @property
    def base(self):
        if not hasattr(self, "_server"):
            return

        host = self._server.host or "0.0.0.0"
        port = self._server.port or 80
        scheme = self.scheme
        secure = self._server.secure

        tpl = "%s://%s%s"

        if (port == 80 and not secure) or (port == 443 and secure):
            port = ""
        else:
            port = ":%d" % port

        return tpl % (scheme, host, port)

    @handler("stream")
    def _on_stream(self, response, data):
        if data is not None:
            if data:
                if response.chunked:
                    data = "{0:s}\r\n{1:s}\r\n".format(
                        hex(len(data))[2:], data
                    ).encode(self._encoding)
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
            del self._clients[response.request.sock]
            response.done = True

    @handler("response")
    def _on_response(self, response):
        """``Response`` Event Handler

        :param response: the ``Response`` object created when the
            HTTP request was initially received.
        :type response: :class:`~circuits.web.wrappers.Response`

        This handler builds an HTTP response data stream from
        the information contained in the *response* object and
        sends it to the client (firing ``Write`` events).
        """
        # send HTTP response status line and headers
        self.fire(
            Write(response.request.sock, b(str(response), self._encoding))
        )

        # process body
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
                parts = (
                    s
                    if isinstance(s, bytes) else s.encode(self._encoding)
                    for s in response.body if s is not None
                )
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
                # Delete the request/response objects if present
                if response.request.sock in self._clients:
                    del self._clients[response.request.sock]
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

        if sock in self._buffers:
            parser = self._buffers[sock]
        else:
            self._buffers[sock] = parser = HttpParser(0, True, self._encoding)

            # If we receive an SSL handshake at the start of a request
            # and we're not a secure server, then immediately close the
            # client connection since we can't respond to it anyway.

            if is_ssl_handshake(data) and not self._server.secure:
                if sock in self._buffers:
                    del self._buffers[sock]
                if sock in self._clients:
                    del self._clients[sock]
                return self.fire(Close(sock))

        _scheme = "https" if self._server.secure else "http"
        parser.execute(data, len(data))
        if not parser.is_headers_complete():
            if parser.errno is not None:
                if parser.errno == BAD_FIRST_LINE:
                    request = wrappers.Request(
                        sock, "GET", _scheme, "/", (1, 1), ""
                    )
                else:
                    request = wrappers.Request(
                        sock, parser.get_method(),
                        parser.get_scheme() or _scheme,
                        parser.get_path(),
                        parser.get_version(),
                        parser.get_query_string()
                    )
                request.server = self._server
                response = wrappers.Response(request, encoding=self._encoding)
                del self._buffers[sock]
                return self.fire(HTTPError(request, response, 400))
            return

        if sock in self._clients:
            request, response = self._clients[sock]
        else:
            method = parser.get_method()
            scheme = parser.get_scheme() or _scheme
            path = parser.get_path()
            version = parser.get_version()
            query_string = parser.get_query_string()

            request = wrappers.Request(
                sock, method, scheme, path, version, query_string
            )
            request.server = self._server

            response = wrappers.Response(request, encoding=self._encoding)

            self._clients[sock] = (request, response)

            rp = request.protocol
            sp = self.protocol

            if rp[0] != sp[0]:
                # the mayor HTTP version differs
                return self.fire(HTTPError(request, response, 505))

            request.headers = parser.get_headers()

            response.protocol = "HTTP/{0:d}.{1:d}".format(*min(rp, sp))
            response.close = not parser.should_keep_alive()

        clen = int(request.headers.get("Content-Length", "0"))
        if clen and not parser.is_message_complete():
            return

        if hasattr(sock, "getpeercert"):
            peer_cert = sock.getpeercert()
            if peer_cert:
                req = Request(request, response, peer_cert)
            else:
                req = Request(request, response)
        else:
            req = Request(request, response)

        # Guard against unwanted request paths (SECURITY).
        path = realpath(request.path)
        if path.rstrip("/") != request.path.rstrip("/"):
            return self.fire(Redirect(request, response, [path], 301))
        else:
            request.body = BytesIO(parser.recv_body())

        del self._buffers[sock]

        self.fire(req)

    @handler("httperror")
    def _on_httperror(self, event, request, response, code, **kwargs):
        """Default HTTP Error Handler

        Default Error Handler that by default just fires a ``Response``
        event with the *response* as argument. The *response* is normally
        modified by a :class:`~circuits.web.errors.HTTPError` instance
        or a subclass thereof.
        """
        response.body = str(event)
        self.fire(Response(response))

    @handler("request_success")
    def _on_request_success(self, e, value):
        """
        Handler for the ``RequestSuccess`` event that is automatically
        generated after all handlers for a
        :class:`~circuits.web.events.Request` event have been invoked
        successfully.

        :param e: the successfully handled ``Request`` event (having
            as attributes the associated
            :class:`~circuits.web.wrappers.Request` and
            :class:`~circuits.web.wrappers.Response` objects).
        :param value: the value(s) returned by the invoked handler(s).

        This handler converts the value(s) returned by the
        (successfully invoked) handlers for the initial ``Request``
        event to a body and assigns it to the ``Response`` object's
        ``body`` attribute. It then fires a
        :class:`~circuits.web.events.Response` event with the
        ``Response`` object as argument.
        """
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
                    self.fire(
                        Redirect(request, response, evalue.urls, evalue.code)
                    )
                elif isinstance(evalue, HTTPException):
                    if evalue.traceback:
                        self.fire(
                            HTTPError(
                                request, response, evalue.code,
                                description=evalue.description,
                                error=error
                            )
                        )
                    else:
                        self.fire(
                            HTTPError(
                                request, response, evalue.code,
                                description=evalue.description
                            )
                        )
                else:
                    self.fire(HTTPError(request, response, error=error))
            else:
                # We want to be notified of changes to the value
                value = e.value.getValue(recursive=False)
                value.event = e
                value.notify = True
        elif isinstance(value, tuple):
            etype, evalue, traceback = error = value

            if isinstance(evalue, RedirectException):
                self.fire(
                    Redirect(request, response, evalue.urls, evalue.code)
                )
            elif isinstance(evalue, HTTPException):
                if evalue.traceback:
                    self.fire(
                        HTTPError(
                            request, response, evalue.code,
                            description=evalue.description,
                            error=error
                        )
                    )
                else:
                    self.fire(
                        HTTPError(
                            request, response, evalue.code,
                            description=evalue.description
                        )
                    )
            else:
                self.fire(HTTPError(request, response, error=error))
        elif not isinstance(value, bool):
            response.body = value
            self.fire(Response(response))

    @handler("error")
    def _on_error(self, etype, evalue, etraceback, handler=None, fevent=None):
        if isinstance(fevent, Response):
            response = fevent.args[0]
            sock = response.request.sock
        else:
            sock = fevent.args[0]

        try:
            request = wrappers.Request(sock, "", "", "", (1, 1), "")
        except:
            # If we can't work with the socket, do nothing.
            return

        request.server = self._server

        response = wrappers.Response(request, encoding=self._encoding)

        self.fire(
            HTTPError(
                request, response, error=(etype, evalue, etraceback)
            )
        )

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
            self.fire(
                Redirect(request, response, evalue.urls, evalue.code)
            )
        elif isinstance(evalue, HTTPException):
            if evalue.traceback:
                self.fire(
                    HTTPError(
                        request, response, evalue.code,
                        description=evalue.description,
                        error=err
                    )
                )
            else:
                self.fire(
                    HTTPError(
                        request, response, evalue.code,
                        description=evalue.description
                    )
                )
        else:
            self.fire(HTTPError(request, response, error=err))
