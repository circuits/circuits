
from io import BytesIO

from circuits.web.parsers import HttpParser
from circuits.web.constants import HTTP_STATUS_CODES
from circuits.core import handler, BaseComponent, Event


class Request(Event):
    """Request Event"""


class Response(Event):
    """Response Event"""


class ResponseObject(object):

    def __init__(self, headers, status, version):
        self.headers = headers
        self.status = status
        self.version = version

        self.body = BytesIO()
        self.reason = HTTP_STATUS_CODES[self.status]

    def __repr__(self):
        return "<Response {0:d} {1:s} {2:s} ({3:d})>".format(
            self.status,
            self.reason,
            self.headers["Content-Type"],
            len(self.body.getvalue())
        )

    def read(self):
        return self.body.read()


class HTTP(BaseComponent):

    channel = "web"

    def __init__(self, encoding="utf-8", channel=channel):
        super(HTTP, self).__init__(channel=channel)

        self._encoding = encoding

        self._response = None
        self._parser = HttpParser(1, True, self._encoding)

    @handler("read")
    def _on_client_read(self, data):
        self._parser.execute(data, len(data))
        if self._parser.errno is not None:
            print("ParserError:", self._parser.error)

        if self._parser.is_message_complete():
            status = self._parser.get_status_code()
            version = self._parser.get_version()
            headers = self._parser.get_headers()

            self._response = ResponseObject(headers, status, version)
            self._response.body.write(self._parser.recv_body())
            self._response.body.seek(0)
            self._parser = HttpParser(1, True, self._encoding)
            self.fire(Response(self._response))
