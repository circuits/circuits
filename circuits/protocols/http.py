from io import BytesIO

import httoop
import httoop.client

from circuits.core import BaseComponent, Event, handler


class request(Event):
    """request Event"""


class response(Event):
    """response Event"""


class ResponseObject:
    def __init__(self, headers, status, version):
        self.headers = headers
        self.status = status
        self.version = version
        self.body = BytesIO()
        self.reason = ''

    def __repr__(self):
        return '<Response {:d} {} {} ({:d})>'.format(
            self.status, self.reason, self.headers.get('Content-Type'), len(self.body.getvalue())
        )

    def read(self):
        return self.body.read()


class HTTP(BaseComponent):
    """A HTTP Client"""

    channel = 'web'

    def __init__(self, encoding='utf-8', channel=channel):
        super().__init__(channel=channel)
        self._encoding = encoding
        self._parser = httoop.client.ClientStateMachine()

    @handler('read')
    def _on_client_read(self, data):
        self._parser.request = httoop.Request()
        for resp in self._parser.parse(data):
            res = ResponseObject(resp.headers, int(resp.status), tuple(resp.protocol))
            res.reason = resp.status.reason
            res.body = resp.body.fd
            self.fire(response(res))
