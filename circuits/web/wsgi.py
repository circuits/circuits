# Module:   wsgi
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WSGI Components

This module implements WSGI Components.
"""

import warnings
from urllib import unquote
from cStringIO import StringIO
from traceback import format_exc

from circuits import handler, Component

import wrappers
from headers import Headers
from utils import quoteHTML
from dispatchers import Dispatcher
from events import Request, Response
from errors import HTTPError, NotFound
from constants import RESPONSES, DEFAULT_ERROR_MESSAGE

class Application(Component):

    headerNames = {
            "HTTP_CGI_AUTHORIZATION": "Authorization",
            "CONTENT_LENGTH": "Content-Length",
            "CONTENT_TYPE": "Content-Type",
            "REMOTE_HOST": "Remote-Host",
            "REMOTE_ADDR": "Remote-Addr",
            }

    def __init__(self):
        super(Application, self).__init__()

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
        request = wrappers.Request(None,
                env("REQUEST_METHOD"),
                env("wsgi.url_scheme"),
                env("PATH_INFO"),
                protocol,
                env("QUERY_STRING"))

        request.remote = wrappers.Host(env("REMOTE_ADDR"), env("REMTOE_PORT"))

        request.headers = headers
        request.script_name = env("SCRIPT_NAME")
        request.wsgi_environ = environ
        request.body = env("wsgi.input")

        response = wrappers.Response(None, request)
        response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

        return request, response

    def setError(self, response, status, message=None, traceback=None):
        try:
            short, long = RESPONSES[status]
        except KeyError:
            short, long = "???", "???"

        if message is None:
            message = short

        explain = long

        content = DEFAULT_ERROR_MESSAGE % {
            "status": status,
            "message": quoteHTML(message),
            "traceback": traceback or ""}

        response.body = content
        response.status = "%s %s" % (status, message)

    def _handleError(self, error):
        response = error.response

        v = self.send(error, "httperror", self.channel)

        if v:
            if issubclass(type(v), basestring):
                response.body = v
                res = Response(response)
                self.send(res, "response", self.channel)
            elif isinstance(v, HTTPError):
                self.send(Response(v.response), "response", self.channel)
            else:
                assert v, "type(v) == %s" % type(v)

    def response(self, response):
        response.done = True

    def __call__(self, environ, start_response, exc_info=None):
        request, response = self.getRequestResponse(environ)

        try:
            req = Request(request, response)

            v = self.send(req, "request", self.channel, errors=True)

            if v:
                if issubclass(type(v), basestring):
                    response.body = v
                    res = Response(response)
                    self.send(res, "response", self.channel)
                elif isinstance(v, HTTPError):
                    self._handleError(v)
                elif isinstance(v, wrappers.Response):
                    res = Response(v)
                    self.send(res, "response", self.channel)
                else:
                    assert v, "type(v) == %s" % type(v)
            else:
                error = NotFound(request, response)
                self._handleError(error)
        except:
            error = HTTPError(request, response, 500, error=format_exc())
            self._handleError(error)
        finally:
            body = response.process()
            start_response(response.status, response.headers.items(), exc_info)
            return [body]

class Gateway(Component):

    def __init__(self, app, path=""):
        channel = None if not path else path
        super(Gateway, self).__init__(channel=channel)

        self.app = app
        self.path = path

        self._errors = StringIO()

        self._request = self._response = None

    def _createEnviron(self):
        environ = {}
        req = self._request
        env = environ.__setitem__

        env("REQUEST_METHOD", req.method)
        env("SERVER_NAME", req.host.split(":", 1)[0])
        env("SERVER_PORT", "%i" % req.server.port)
        env("SERVER_PROTOCOL", "HTTP/%d.%d" % req.server_protocol)
        env("QUERY_STRING", req.qs)
        env("SCRIPT_NAME", req.script_name)
        env("CONTENT_TYPE", req.headers.get("Content-Type", ""))
        env("CONTENT_LENGTH", req.headers.get("Content-Length", ""))
        env("REMOTE_ADDR", req.remote.ip)
        env("REMOTE_PORT", "%i" % req.remote.port)
        env("wsgi.version", (1, 0))
        env("wsgi.input", req.body)
        env("wsgi.errors", self._errors)
        env("wsgi.multithread", False)
        env("wsgi.multiprocess", False)
        env("wsgi.run_once", False)
        env("wsgi.url_scheme", req.scheme)

        if req.path:
            i = req.path.find(self.path) + len(self.path)
            req.script_name, req.path = req.path[:i], req.path[i:]
            env("SCRIPT_NAME", req.script_name)
            env("PATH_INFO", unquote(req.path))

        for k, v in req.headers.items():
            env("HTTP_%s" % k.upper().replace("-", "_"), v)

        return environ

    def start_response(self, status, headers, exc_info=None):
        self._response.status = status
        for header in headers:
            self._response.headers.add_header(*header)

    @handler("request", filter=True)
    def request(self, request, response):
        self._request = request
        self._response = response

        return "".join(self.app(self._createEnviron(), self.start_response))
