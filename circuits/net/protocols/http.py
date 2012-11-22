
from io import BytesIO

from circuits.web.headers import parse_headers
from circuits.core import handler, BaseComponent, Event


class Request(Event):
    """Request Event"""


class Response(Event):
    """Response Event"""


class ResponseObject(object):

    def __init__(self, status, message, protocol=None):
        self.status = status
        self.message = message
        self.protocol = protocol

        self._headers = None
        self._body = BytesIO()

    @property
    def headers(self):
        return self._headers

    def read(self):
        return self._body.read()


class HTTP(BaseComponent):

    channel = "web"

    def __init__(self, encoding="utf-8", channel=channel):
        super(HTTP, self).__init__(channel=channel)

        self._encoding = encoding

        self._response = None
        self._buffer = BytesIO()

    @handler("read")
    def _on_client_read(self, data):
        if self._response is not None:
            self._response._body.write(data)
            cLen = int(self._response.headers.get("Content-Length", "0"))
            if cLen and self._response._body.tell() == cLen:
                self._response._body.seek(0)
                self.fire(Response(self._response))
                self._response = None
        else:
            statusline, data = data.split(b"\r\n", 1)
            statusline = statusline.strip().decode(
                    self._encoding, "replace")
            protocol, status, message = statusline.split(" ", 2)

            status = int(status)
            protocol = tuple(map(int, protocol[5:].split(".")))

            response = ResponseObject(status, message, protocol)

            end_of_headers = data.find(b"\r\n\r\n")
            header_data = data[:end_of_headers].decode(
                    self._encoding, "replace")
            headers = response._headers = parse_headers(header_data)

            response._body.write(data[(end_of_headers + 4):])

            cLen = int(headers.get("Content-Length", "0"))
            if cLen and response._body.tell() < cLen:
                self._response = response
                return

            response._body.seek(0)
            self.fire(Response(response))
