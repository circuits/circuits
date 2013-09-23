
from io import BytesIO

from circuits.web.parsers import HttpParser
from circuits.web.constants import HTTP_STATUS_CODES
from circuits.core import handler, BaseComponent, Event


class request(Event):
    """request Event"""


class response(Event):
    """response Event"""


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

        self._parser = HttpParser(1, True, self._encoding)

    @handler("read")
    def _on_client_read(self, data):
        self._parser.execute(data, len(data))
        if self._parser.is_message_complete() or \
                (self._parser.is_headers_complete() and
                 self._parser._clen == 0):
            status = self._parser.get_status_code()
            version = self._parser.get_version()
            headers = self._parser.get_headers()

            res = ResponseObject(headers, status, version)
            res.body.write(self._parser.recv_body())
            res.body.seek(0)
            self.fire(response(res))

            self._parser = HttpParser(1, True, self._encoding)
