
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from circuits.web.headers import parseHeaders
from circuits.core import handler, BaseComponent, Event

class Request(Event):
    """Request Event"""

    success = "request_success",
    failure = "request_failure",

class Response(Event):
    """Response Event"""

class ResponseObject(object):

    def __init__(self, status, message, protocol=None):
        self.status = status
        self.message = message
        self.protocol = protocol

        self._headers = None
        self._body = StringIO()

    @property
    def headers(self):
        return self._headers

    def read(self):
        return self._body.read()

class HTTP(BaseComponent):

    channel = "web"

    def __init__(self, channel=channel):
        super(HTTP, self).__init__(channel=channel)

        self._response = None
        self._buffer = StringIO()

    @handler("read", target="client")
    def _on_client_read(self, data):
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
            protocol, status, message = statusline.split(" ", 2)

            status = int(status)
            protocol = tuple(map(int, protocol[5:].split(".")))

            response = ResponseObject(status, message, protocol)

            headers, body = parseHeaders(StringIO(data))
            response._headers = headers
            response._body.write(body)

            cLen = int(headers.get("Content-Length", "0"))
            if cLen and response._body.tell() < cLen:
                self._response = response
                return

            response._body.seek(0)
            self.push(Response(response))
