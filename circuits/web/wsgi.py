"""WSGI Components

This module implements WSGI Components.
"""
from operator import itemgetter
from sys import exc_info as _exc_info
from traceback import format_tb
from types import GeneratorType

from circuits.core import BaseComponent, handler
from circuits.tools import tryimport
from circuits.web import wrappers

from .dispatchers import Dispatcher
from .errors import httperror
from .events import request
from .headers import Headers
from .http import HTTP

StringIO = tryimport(("cStringIO", "StringIO", "io"), "StringIO")


def create_environ(errors, path, req):
    environ = {}
    env = environ.__setitem__

    env("REQUEST_METHOD", req.method)
    env("SERVER_NAME", req.host.split(":", 1)[0])
    env("SERVER_PORT", "%i" % (req.server.port or 0))
    env("SERVER_PROTOCOL", "HTTP/%d.%d" % req.server.http.protocol)
    env("QUERY_STRING", req.qs)
    env("SCRIPT_NAME", req.script_name)
    env("CONTENT_TYPE", req.headers.get("Content-Type", ""))
    env("CONTENT_LENGTH", req.headers.get("Content-Length", ""))
    env("REMOTE_ADDR", req.remote.ip)
    env("REMOTE_PORT", "%i" % (req.remote.port or 0))
    env("wsgi.version", (1, 0))
    env("wsgi.input", req.body)
    env("wsgi.errors", errors)
    env("wsgi.multithread", False)
    env("wsgi.multiprocess", False)
    env("wsgi.run_once", False)
    env("wsgi.url_scheme", req.scheme)

    if req.path:
        req.script_name = req.path[:len(path)]
        req.path = req.path[len(path):]
        env("SCRIPT_NAME", req.script_name)
        env("PATH_INFO", req.path)

    for k, v in list(req.headers.items()):
        env("HTTP_%s" % k.upper().replace("-", "_"), v)

    return environ


class Application(BaseComponent):

    channel = "web"

    headerNames = {
        "HTTP_CGI_AUTHORIZATION": "Authorization",
        "CONTENT_LENGTH": "Content-Length",
        "CONTENT_TYPE": "Content-Type",
        "REMOTE_HOST": "Remote-Host",
        "REMOTE_ADDR": "Remote-Addr",
    }

    def init(self):
        self._finished = False

        HTTP(self).register(self)
        Dispatcher().register(self)

    def translateHeaders(self, environ):
        for cgiName in environ:
            # We assume all incoming header keys are uppercase already.
            if cgiName in self.headerNames:
                yield self.headerNames[cgiName], environ[cgiName]
            elif cgiName[:5] == "HTTP_":
                # Hackish attempt at recovering original header names.
                translatedHeader = cgiName[5:].replace("_", "-")
                yield translatedHeader, environ[cgiName]

    def getRequestResponse(self, environ):
        env = environ.get

        headers = Headers(list(self.translateHeaders(environ)))

        protocol = tuple(map(int, env("SERVER_PROTOCOL")[5:].split(".")))
        req = wrappers.Request(
            None,
            env("REQUEST_METHOD"),
            env("wsgi.url_scheme"),
            env("PATH_INFO", ""),
            protocol,
            env("QUERY_STRING", ""),
            headers=headers
        )

        req.remote = wrappers.Host(env("REMOTE_ADDR"), env("REMTOE_PORT"))
        req.script_name = env("SCRIPT_NAME")
        req.wsgi_environ = environ

        try:
            cl = int(headers.get("Content-Length", "0"))
        except ValueError:
            cl = 0

        req.body.write(env("wsgi.input").read(cl))  # FIXME: what about chunked encoding?
        req.body.seek(0)

        res = wrappers.Response(req)
        res.gzip = "gzip" in req.headers.get("Accept-Encoding", "")

        return req, res

    def __call__(self, environ, start_response, exc_info=None):
        self.request, self.response = self.getRequestResponse(environ)
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

    @handler("response", channel="web")
    def on_response(self, event, response):
        self._finished = True
        event.stop()

    @property
    def host(self):
        return ""

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

    channel = "web"

    def init(self, apps):
        self.apps = apps

        self.errors = dict((k, StringIO()) for k in self.apps.keys())

    @handler("request", priority=0.2)
    def _on_request(self, event, req, res):
        if not self.apps:
            return

        parts = req.path.split("/")

        candidates = []
        for i in range(len(parts)):
            k = "/".join(parts[:(i + 1)]) or "/"
            if k in self.apps:
                candidates.append((k, self.apps[k]))
        candidates = sorted(candidates, key=itemgetter(0), reverse=True)

        if not candidates:
            return

        path, app = candidates[0]

        buffer = StringIO()

        def start_response(status, headers, exc_info=None):
            res.status = int(status.split(" ", 1)[0])
            for header in headers:
                res.headers.add_header(*header)
            return buffer.write

        errors = self.errors[path]

        environ = create_environ(errors, path, req)

        try:
            body = app(environ, start_response)
            if isinstance(body, list):
                _body = type(body[0])() if body else ""
                body = _body.join(body)
            elif isinstance(body, GeneratorType):
                res.body = body
                res.stream = True
                return res

            if not body:
                if not buffer.tell():
                    return empty
                else:
                    buffer.seek(0)
                    return buffer
            else:
                return body
        except Exception as error:
            etype, evalue, etraceback = _exc_info()
            error = (etype, evalue, format_tb(etraceback))
            return httperror(req, res, 500, error=error)
        finally:
            event.stop()
