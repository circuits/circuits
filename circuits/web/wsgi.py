"""
WSGI Components

This module implements WSGI Components.
"""

from io import StringIO
from operator import itemgetter
from sys import exc_info as _exc_info
from traceback import format_tb

import httoop
from httoop.gateway.wsgi import WSGI

from circuits.core import BaseComponent, handler
from circuits.web import wrappers

from .dispatchers import Dispatcher
from .errors import httperror
from .events import request
from .http import HTTP


class WSGIGateway(WSGI):
    def __init__(self, req, res, errors, path):
        self.req = req
        self.__errors = errors
        self.__path = path
        self.request = req.to_httoop()
        self.response = res.to_httoop()
        # super().__init__()
        # self.set_environ(self.get_environ())
        # return
        environ = WSGIClient()
        environ.request = self.request
        super().__init__(environ.get_environ())

    def get_environ(self):
        environ = super().get_environ()
        env = environ.__setitem__
        req = self.req

        env('SERVER_NAME', req.host.split(':', 1)[0])
        env('SERVER_PORT', '%i' % (req.server.port or 0))
        env('SERVER_PROTOCOL', 'HTTP/%d.%d' % req.server.http.protocol)
        env('SCRIPT_NAME', req.script_name)
        env('REMOTE_ADDR', req.remote.ip)
        env('REMOTE_PORT', '%i' % (req.remote.port or 0))
        env('wsgi.errors', self.__errors)
        env('wsgi.run_once', False)

        if req.path:
            req.script_name = req.path[: len(self.__path)]
            req.path = req.path[len(self.__path) :]
            env('SCRIPT_NAME', req.script_name)
            env('PATH_INFO', req.path)

        return environ


class WSGIClient(WSGI):
    def __init__(self, *args, **kwargs):
        self.request = httoop.Request()
        self.response = httoop.Response()
        super().__init__(*args, **kwargs)


class Application(BaseComponent):
    channel = 'web'

    def init(self):
        self._finished = False

        HTTP(self).register(self)
        Dispatcher().register(self)

    def __call__(self, environ, start_response, exc_info=None):
        wsgi = WSGIClient(environ, use_path_info=False)
        for key, value in {
            'HTTP_CGI_AUTHORIZATION': 'Authorization',
            'REMOTE_HOST': 'Remote-Host',
            'REMOTE_ADDR': 'Remote-Addr',
        }.items():
            if key in environ:
                wsgi.request.headers.append(value, environ[key])

        self.request = wrappers.Request.from_httoop(wsgi.request, None)
        self.request.path = wsgi.path_info
        self.response = wrappers.Response.from_httoop(wsgi.response, self.request)
        self.response.gzip = 'gzip' in self.request.headers.get('Accept-Encoding', '')
        self.request.remote = wrappers.Host(wsgi.remote_address, wsgi.remote_port)
        self.request.script_name = wsgi.script_name
        self.request.wsgi_environ = environ

        self.fire(request(self.request, self.response))

        self._finished = False
        while self._queue or not self._finished:
            self.tick()

        self.response.prepare()
        body = self.response.body
        status = self.response.status
        headers = list(self.response.headers.items())

        start_response(str(status), headers, exc_info)
        return body

    @handler('response', channel='web')
    def on_response(self, event, response):
        self._finished = True
        event.stop()

    @property
    def host(self):
        return ''

    @property
    def port(self):
        return 0

    @property
    def secure(self):
        return False


class _Empty(str):
    def __bool__(self):
        return True

    __nonzero__ = __bool__


empty = _Empty()
del _Empty


class Gateway(BaseComponent):
    channel = 'web'

    def init(self, apps):
        self.apps = apps

        self.errors = {k: StringIO() for k in self.apps.keys()}

    @handler('request', priority=0.2)
    def _on_request(self, event, req, res):
        if not self.apps:
            return

        parts = req.path.split('/')

        candidates = []
        for i in range(len(parts)):
            k = '/'.join(parts[: (i + 1)]) or '/'
            if k in self.apps:
                candidates.append((k, self.apps[k]))
        candidates = sorted(candidates, key=itemgetter(0), reverse=True)

        if not candidates:
            return

        path, app = candidates[0]

        errors = self.errors[path]

        wsgi = WSGIGateway(req, res, errors, path)

        try:
            result = wsgi(app)
            res.__dict__.update(res.from_httoop(wsgi.response, req).__dict__)
            if (not result or result == ['']) and wsgi.response.body.fileable and wsgi.response.body.fd.tell():
                res.chunked = False
                res.stream = True

                def body_func():
                    yield from wsgi.response.body

                res.body = body_func()
                return res
            elif not wsgi.response.body:
                return empty
            return res
        except Exception:
            etype, evalue, etraceback = _exc_info()
            error = (etype, evalue, format_tb(etraceback))
            return httperror(req, res, 500, error=error)
        finally:
            event.stop()
