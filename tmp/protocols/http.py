#!/usr/bin/python -i

from StringIO import StringIO

from circuits.web.headers import parseHeaders, Headers
from circuits.core import handler, BaseComponent, Event
from circuits.net.sockets import TCPClient, Connect, Write, Close

class Request(Event):
    """Request Event"""

    success = "request_success",
    failure = "request_failure",

class Response(Event):
    """Response Event"""

class ResponseObject(object):

    def __init__(self, status, reason, protocol=None):
        self.status = status
        self.reason = reason
        self.protocol = protocol

        self._headers = None
        self._body = StringIO()

    @property
    def headers(self):
        return self._headers

    def read(self):
        return self._body.read()

class HTTPException(Exception):
    pass

class NotConnected(HTTPException):
    pass

class HTTP(BaseComponent):

    channel = "http"

    def __init__(self, *args, **kwargs):
        super(HTTP, self).__init__(*args, **kwargs)

        self._response = None
        self._buffer = StringIO()

    @handler("read", target="client")
    def onClientRead(self, data):
        if self._response is not None:
            self._response._body.write(data)
            cLen = int(self._response.headers.get("Content-Length", "0"))
            if cLen and self._response._body.tell() == cLen:
                self._response._body.seek(0)
                self.push(Response(self._response))
                self._response = None
        else:
            statusline, data = data.split("\n", 1)
            statusline = statusline.strip()
            protocol, status, reason = statusline.split(" ", 2)

            status = int(status)
            protocol = tuple(map(int, protocol[5:].split(".")))

            response = ResponseObject(status, reason, protocol)

            headers, body = parseHeaders(StringIO(data))
            response._headers = headers
            response._body.write(body)

            cLen = int(headers.get("Content-Length", "0"))
            if cLen and response._body.tell() < cLen:
                self._response = response
                return

            response._body.seek(0)
            self.push(Response(response))

class Client(BaseComponent):

    def __init__(self, host, port):
        super(Client, self).__init__()

        self.host = host
        self.port = port

        self._response = None

        self._transport = TCPClient()
        self._transport.register(self)

        HTTP().register(self._transport)

    def close(self):
        if self._transport.connected:
            self.push(Close(), target=self._transport)

    def connect(self):
        if not self._transport.connected:
            self.push(Connect(self.host, self.port), target=self._transport)

    def request(self, method, url, body=None, headers={}):
        if self._transport.connected:
            self.push(Request(method, url, body, headers))
        else:
            raise NotConnected()

    @handler("request")
    def onRequest(self, method, url, body=None, headers={}):
        if self._transport.connected:
            headers = Headers([(k, v) for k, v in headers.items()])
            command = "%s %s HTTP/1.1" % (method, url)
            message = "%s\r\n%s" % (command, headers)
            self.push(Write(message), target=self._transport)
            if body:
                self.push(Write(body), target=self._transport)
        else:
            raise NotConnected()

    @handler("response")
    def onResponse(self, response):
        self._response = response
        if not response.status == 100:
            self.push(Close(), target=self._transport)

    @property
    def response(self):
        if hasattr(self, "_response"):
            return self._response
