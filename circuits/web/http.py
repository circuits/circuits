"""Hyper Text Transfer Protocol

This module implements the server side Hyper Text Transfer Protocol
or commonly known as HTTP.
"""
from io import BytesIO
from socket import socket

from circuits.core import BaseComponent, Value, handler
from circuits.net.events import close, write
from circuits.net.utils import is_ssl_handshake
from circuits.six import text_type
from circuits.six.moves.urllib_parse import quote

from . import wrappers
from .constants import SERVER_PROTOCOL, SERVER_VERSION
from .errors import httperror, notfound, redirect
from .events import request, response, stream
from .exceptions import HTTPException, Redirect as RedirectException
from .parsers import BAD_FIRST_LINE, HttpParser
from .url import parse_url
from .utils import is_unix_socket

MAX_HEADER_FRAGENTS = 20
HTTP_ENCODING = 'utf-8'


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

        self._uri = None
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
        return "https" if self._server.secure else "http"

    @property
    def base(self):
        if self.uri is None:
            return ""
        return self.uri.utf8().rstrip(b"/").decode(self._encoding)

    @property
    def uri(self):
        return self._uri

    @handler("ready", priority=1.0)
    def _on_ready(self, server, bind):
        if is_unix_socket(server.host):
            url = server.host
        else:
            url = "{0:s}://{1:s}{2:s}".format(
                (server.secure and "https") or "http",
                server.host or "0.0.0.0",
                ":{0:d}".format(server.port or 80)
                if server.port not in (80, 443)
                else ""
            )

        self._uri = parse_url(url)

    @handler("stream")  # noqa
    def _on_stream(self, res, data):
        sock = res.request.sock

        if data is not None:
            if isinstance(data, text_type):
                data = data.encode(self._encoding)

            if res.chunked:
                buf = [
                    hex(len(data))[2:].encode(self._encoding),
                    b"\r\n",
                    data,
                    b"\r\n"
                ]
                data = b"".join(buf)

            self.fire(write(sock, data))

            if res.body and not res.done:
                try:
                    data = next(res.body)
                    while not data:  # Skip over any null byte sequences
                        data = next(res.body)
                except StopIteration:
                    data = None
                self.fire(stream(res, data))
        else:
            if res.body:
                res.body.close()
            if res.chunked:
                self.fire(write(sock, b"0\r\n\r\n"))
            if res.close:
                self.fire(close(sock))
            if sock in self._clients:
                del self._clients[sock]

            res.done = True

    @handler("response")  # noqa
    def _on_response(self, res):
        """``Response`` Event Handler

        :param response: the ``Response`` object created when the
            HTTP request was initially received.
        :type response: :class:`~circuits.web.wrappers.Response`

        This handler builds an HTTP response data stream from
        the information contained in the *response* object and
        sends it to the client (firing ``write`` events).
        """
        # send HTTP response status line and headers

        req = res.request
        headers = res.headers
        sock = req.sock

        if req.method == "HEAD":
            self.fire(write(sock, bytes(res)))
            self.fire(write(sock, bytes(headers)))
        elif res.stream and res.body:
            try:
                data = next(res.body)
            except StopIteration:
                data = None
            self.fire(write(sock, bytes(res)))
            self.fire(write(sock, bytes(headers)))
            self.fire(stream(res, data))
        else:
            self.fire(write(sock, bytes(res)))
            self.fire(write(sock, bytes(headers)))

            if isinstance(res.body, bytes):
                body = res.body
            elif isinstance(res.body, text_type):
                body = res.body.encode(self._encoding)
            else:
                parts = (
                    s
                    if isinstance(s, bytes) else s.encode(self._encoding)
                    for s in res.body if s is not None
                )
                body = b"".join(parts)

            if body:
                if res.chunked:
                    buf = [
                        hex(len(body))[2:].encode(self._encoding),
                        b"\r\n",
                        body,
                        b"\r\n"
                    ]
                    body = b"".join(buf)

                self.fire(write(sock, body))

                if res.chunked:
                    self.fire(write(sock, b"0\r\n\r\n"))

            if not res.stream:
                if res.close:
                    self.fire(close(sock))
                # Delete the request/response objects if present
                if sock in self._clients:
                    del self._clients[sock]
                res.done = True

    @handler("disconnect")
    def _on_disconnect(self, sock):
        if sock in self._clients:
            del self._clients[sock]

    @handler("read")  # noqa
    def _on_read(self, sock, data):
        """Read Event Handler

        Process any incoming data appending it to an internal buffer.
        Split the buffer by the standard HTTP delimiter CRLF and create
        Raw Event per line. Any unfinished lines of text, leave in the buffer.
        """

        if sock in self._buffers:
            parser = self._buffers[sock]
        else:
            self._buffers[sock] = parser = HttpParser(0, True)

            # If we receive an SSL handshake at the start of a request
            # and we're not a secure server, then immediately close the
            # client connection since we can't respond to it anyway.

            if is_ssl_handshake(data) and not self._server.secure:
                if sock in self._buffers:
                    del self._buffers[sock]
                if sock in self._clients:
                    del self._clients[sock]
                return self.fire(close(sock))

        _scheme = "https" if self._server.secure else "http"
        parser.execute(data, len(data))
        if not parser.is_headers_complete():
            if parser.errno is not None:
                if parser.errno == BAD_FIRST_LINE:
                    req = wrappers.Request(sock, server=self._server)
                else:
                    req = wrappers.Request(
                        sock,
                        parser.get_method(),
                        parser.get_scheme() or _scheme,
                        parser.get_path(),
                        parser.get_version(),
                        parser.get_query_string(),
                        server=self._server
                    )
                req.server = self._server
                res = wrappers.Response(req, encoding=self._encoding)
                del self._buffers[sock]
                return self.fire(httperror(req, res, 400))
            return

        if sock in self._clients:
            req, res = self._clients[sock]
        else:
            method = parser.get_method()
            scheme = parser.get_scheme() or _scheme
            path = parser.get_path()
            version = parser.get_version()
            query_string = parser.get_query_string()

            req = wrappers.Request(
                sock, method, scheme, path, version, query_string,
                headers=parser.get_headers(), server=self._server
            )

            res = wrappers.Response(req, encoding=self._encoding)

            self._clients[sock] = (req, res)

            rp = req.protocol
            sp = self.protocol

            if rp[0] != sp[0]:
                # the major HTTP version differs
                return self.fire(httperror(req, res, 505))

            res.protocol = "HTTP/{0:d}.{1:d}".format(*min(rp, sp))
            res.close = not parser.should_keep_alive()

        clen = int(req.headers.get("Content-Length", "0"))
        if (clen or req.headers.get("Transfer-Encoding") == "chunked") and not parser.is_message_complete():
            return

        if hasattr(sock, "getpeercert"):
            peer_cert = sock.getpeercert()
            if peer_cert:
                e = request(req, res, peer_cert)
            else:
                e = request(req, res)
        else:
            e = request(req, res)

        if req.protocol != (1, 0) and not req.headers.get("Host"):
            del self._buffers[sock]
            return self.fire(httperror(req, res, 400, description="No host header defined"))

        # Guard against unwanted request paths (SECURITY).
        path = req.path
        _path = req.uri._path
        if (path.encode(self._encoding) != _path) and (
                quote(path).encode(self._encoding) != _path):
            return self.fire(
                redirect(req, res, [req.uri.utf8()], 301)
            )

        req.body = BytesIO(parser.recv_body())
        del self._buffers[sock]

        self.fire(e)

    @handler("httperror")
    def _on_httperror(self, event, req, res, code, **kwargs):
        """Default HTTP Error Handler

        Default Error Handler that by default just fires a ``Response``
        event with the *response* as argument. The *response* is normally
        modified by a :class:`~circuits.web.errors.HTTPError` instance
        or a subclass thereof.
        """

        res.body = str(event)
        self.fire(response(res))

    @handler("request_success")  # noqa
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

        req, res = e.args[:2]

        if value is None:
            self.fire(notfound(req, res))
        elif isinstance(value, httperror):
            res.body = str(value)
            self.fire(response(res))
        elif isinstance(value, wrappers.Response):
            self.fire(response(value))
        elif isinstance(value, Value):
            if value.result and not value.errors:
                res.body = value.value
                self.fire(response(res))
            elif value.errors:
                error = value.value
                etype, evalue, traceback = error
                if isinstance(evalue, RedirectException):
                    self.fire(
                        redirect(req, res, evalue.urls, evalue.code)
                    )
                elif isinstance(evalue, HTTPException):
                    if evalue.traceback:
                        self.fire(
                            httperror(
                                req, res, evalue.code,
                                description=evalue.description,
                                error=error
                            )
                        )
                    else:
                        self.fire(
                            httperror(
                                req, res, evalue.code,
                                description=evalue.description
                            )
                        )
                else:
                    self.fire(httperror(req, res, error=error))
            else:
                # We want to be notified of changes to the value
                value = e.value.getValue(recursive=False)
                value.event = e
                value.notify = True
        elif isinstance(value, tuple):
            etype, evalue, traceback = error = value

            if isinstance(evalue, RedirectException):
                self.fire(
                    redirect(req, res, evalue.urls, evalue.code)
                )
            elif isinstance(evalue, HTTPException):
                if evalue.traceback:
                    self.fire(
                        httperror(
                            req, res, evalue.code,
                            description=evalue.description,
                            error=error
                        )
                    )
                else:
                    self.fire(
                        httperror(
                            req, res, evalue.code,
                            description=evalue.description
                        )
                    )
            else:
                self.fire(httperror(req, res, error=error))
        elif not isinstance(value, bool):
            res.body = value
            self.fire(response(res))

    @handler("exception")
    def _on_exception(self, *args, **kwargs):
        if not len(args) == 3:
            return

        etype, evalue, etraceback = args
        fevent = kwargs["fevent"]

        if isinstance(fevent, response):
            res = fevent.args[0]
            req = res.request
        elif isinstance(fevent.value.parent.event, request):
            req, res = fevent.value.parent.event.args[:2]
        elif len(fevent.args[2:]) == 4:
            req, res = fevent.args[2:]
        elif len(fevent.args) == 2 and isinstance(fevent.args[0], socket):
            req = wrappers.Request(fevent.args[0], server=self._server)
            res = wrappers.Response(req, self._encoding, 500)
        else:
            return

        if isinstance(evalue, HTTPException):
            code = evalue.code
        else:
            code = None

        self.fire(
            httperror(
                req, res, code=code, error=(etype, evalue, etraceback)
            )
        )

    @handler("request_failure")
    def _on_request_failure(self, erequest, error):
        req, res = erequest.args

        # Ignore filtered requests already handled (eg: HTTPException(s)).
        if req.handled:
            return

        req.handled = True

        etype, evalue, traceback = error

        if isinstance(evalue, RedirectException):
            self.fire(
                redirect(req, res, evalue.urls, evalue.code)
            )
        elif isinstance(evalue, HTTPException):
            self.fire(
                httperror(
                    req, res, evalue.code,
                    description=evalue.description,
                    error=error
                )
            )
        else:
            self.fire(httperror(req, res, error=error))

    @handler("response_failure")
    def _on_response_failure(self, eresponse, error):
        res = eresponse.args[0]
        req = res.request

        # Ignore failed "response" handlers (eg: Loggers or Tools)
        if res.done:
            return

        res = wrappers.Response(req, self._encoding, 500)
        self.fire(httperror(req, res, error=error))

    @handler("request_complete")
    def _on_request_complete(self, *args, **kwargs):
        """Dummy Event Handler for request events

        - request_complete
        """

    @handler("response_success", "response_complete")
    def _on_response_feedback(self, *args, **kwargs):
        """Dummy Event Handler for response events

        - response_success
        - response_complete
        """

    @handler("stream_success", "stream_failure", "stream_complete")
    def _on_stream_feedback(self, *args, **kwargs):
        """Dummy Event Handler for stream events

        - stream_success
        - stream_failure
        - stream_complete
        """
