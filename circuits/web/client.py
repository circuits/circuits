import httoop

from circuits.core import BaseComponent, Event, handler
from circuits.net.events import close, connect, write
from circuits.net.sockets import TCPClient
from circuits.protocols.http import HTTP


def parse_url(url):
    uri = httoop.URI(url)
    path = uri.path or '/'
    if uri.query_string:
        path = f'{path}?{uri.query_string}'
    return (uri.host, uri.port, path, uri.scheme == 'https')


class HTTPException(Exception):
    pass


class NotConnected(HTTPException):
    pass


class request(Event):
    """
    request Event

    This Event is used to initiate a new request.

    :param method: HTTP Method (PUT, GET, POST, DELETE)
    :type  method: str

    :param url: Request URL
    :type  url: str
    """

    def __init__(self, method, path, body=None, headers=None):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super().__init__(method, path, body, headers)


class Client(BaseComponent):
    channel = 'client'

    def __init__(self, channel=channel):
        super().__init__(channel=channel)
        self._response = None

        self._transport = TCPClient(channel=channel).register(self)

        HTTP(channel=channel).register(self._transport)

    @handler('write')
    def write(self, data):
        if self._transport.connected:
            self.fire(write(data), self._transport)

    @handler('close')
    def close(self):
        if self._transport.connected:
            self.fire(close(), self._transport)

    @handler('connect', priority=1)
    def connect(self, event, host=None, port=None, secure=None):
        if not self._transport.connected:
            self.fire(connect(host, port, secure), self._transport)

        event.stop()

    @handler('request')
    def request(self, method, url, body=None, headers=None):
        req = httoop.Request(method, url, headers, body)
        if not req.uri.path:
            req.uri.path = '/'

        if not self._transport.connected:
            self.fire(connect(req.uri.host, req.uri.port, req.uri.scheme == 'https'))
            yield self.wait('connected', self._transport.channel)

        # Clients MUST include Host header in HTTP/1.1 requests (RFC 2616)
        if 'Host' not in req.headers:
            req.headers['Host'] = '{}{}'.format(req.uri.host, '' if req.uri.port in (80, 443) else f':{req.uri.port:d}')

        if body is not None:
            req.headers['Content-Length'] = str(len(body))

        self.fire(write(b'%s%s' % (req, req.headers)), self._transport)
        if req.body:
            self.fire(write(bytes(req.body)), self._transport)

        yield (yield self.wait('response'))

    @handler('response')
    def _on_response(self, response):
        self._response = response
        if response.headers.get('Connection', '').lower() == 'close':
            self.fire(close(), self._transport)
        return response

    @property
    def connected(self):
        if hasattr(self, '_transport'):
            return self._transport.connected

    @property
    def response(self):
        return getattr(self, '_response', None)
