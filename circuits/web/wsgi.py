# Module:   wsgi
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WSGI Components

This module implements WSGI Components.
"""

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote  # NOQA

from operator import itemgetter
from traceback import format_tb
from sys import exc_info as _exc_info

from circuits.tools import tryimport
from circuits.core import handler, BaseComponent

StringIO = tryimport(("cStringIO", "StringIO", "io"), "StringIO")

from . import wrappers
from .http import HTTP
from .events import Request
from .headers import Headers
from .errors import HTTPError
from .dispatchers import Dispatcher


def create_environ(errors, path, req):
    environ = {}
    env = environ.__setitem__

    env("REQUEST_METHOD", req.method)
    env("SERVER_NAME", req.host.split(":", 1)[0])
    env("SERVER_PORT", "%i" % (req.server.port or 0))
    env("SERVER_PROTOCOL", "HTTP/%d.%d" % req.server_protocol)
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

        HTTP().register(self)
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
        request = wrappers.Request(
            None,
            env("REQUEST_METHOD"),
            env("wsgi.url_scheme"),
            env("PATH_INFO", ""),
            protocol,
            env("QUERY_STRING", "")
        )
        request.server = None

        request.remote = wrappers.Host(env("REMOTE_ADDR"), env("REMTOE_PORT"))

        request.headers = headers
        request.script_name = env("SCRIPT_NAME")
        request.wsgi_environ = environ

        try:
            cl = int(headers.get("Content-Length", "0"))
        except:
            cl = 0

        request.body.write(env("wsgi.input").read(cl))
        request.body.seek(0)

        response = wrappers.Response(request)
        response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

        return request, response

    def __call__(self, environ, start_response, exc_info=None):
        self.request, self.response = self.getRequestResponse(environ)
        self.fire(Request(self.request, self.response))

        self._finished = False
        while self or not self._finished:
            self.tick()

        self.response.prepare()
        body = self.response.body
        status = self.response.status
        headers = list(self.response.headers.items())

        start_response(status, headers, exc_info)
        return body

    @handler("response", filter=True, channel="web")
    def response(self, response):
        self._finished = True
        return True


class _Empty(str):

    def __bool__(self):
        return True

empty = _Empty()
del _Empty


class Gateway(BaseComponent):

    channel = "web"

    def init(self, apps):
        self.apps = apps

        self.errors = dict((k, StringIO()) for k in self.apps.keys())

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, event, request, response):
        if not self.apps:
            return

        parts = request.path.split("/")

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
            response.code = int(status.split(" ", 1)[0])
            for header in headers:
                response.headers.add_header(*header)
            return buffer.write

        errors = self.errors[path]

        environ = create_environ(errors, path, request)

        try:
            body = app(environ, start_response)
            if isinstance(body, list):
                body = "".join(body)

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
            return HTTPError(request, response, 500, error=error)
