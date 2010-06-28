# Module:   wsgi
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WSGI Components

This module implements WSGI Components.
"""

from urllib import unquote
from cStringIO import StringIO
from traceback import format_tb
from sys import exc_info as _exc_info

from circuits.core import handler, BaseComponent

import wrappers
from http import HTTP
from events import Request
from headers import Headers
from errors import HTTPError
from dispatchers import Dispatcher

class Application(BaseComponent):

    headerNames = {
            "HTTP_CGI_AUTHORIZATION": "Authorization",
            "CONTENT_LENGTH": "Content-Length",
            "CONTENT_TYPE": "Content-Type",
            "REMOTE_HOST": "Remote-Host",
            "REMOTE_ADDR": "Remote-Addr",
            }

    def __init__(self):
        super(Application, self).__init__()

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
        request = wrappers.Request(None,
                env("REQUEST_METHOD"),
                env("wsgi.url_scheme"),
                env("PATH_INFO", ""),
                protocol,
                env("QUERY_STRING", ""))
        request.server = None

        request.remote = wrappers.Host(env("REMOTE_ADDR"), env("REMTOE_PORT"))

        request.headers = headers
        request.script_name = env("SCRIPT_NAME")
        request.wsgi_environ = environ
        request.body = env("wsgi.input")

        response = wrappers.Response(None, request)
        response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

        return request, response

    def __call__(self, environ, start_response, exc_info=None):
        self.request, self.response = self.getRequestResponse(environ)
        self.push(Request(self.request, self.response), "request", "web")

        self.run()

        self.response.prepare()
        body = self.response.body
        status = self.response.status
        headers = self.response.headers.items()

        start_response(status, headers, exc_info)
        return body

    @handler("response", filter=True, target="http")
    def response(self, response):
        self.stop()
        return True

class Gateway(BaseComponent):

    channel = "web"

    def __init__(self, app, path="/"):
        super(Gateway, self).__init__()

        self.app = app
        self.path = path

        self._errors = StringIO()

        self._request = self._response = None

        self.addHandler(self._on_request, "request", filter=True,
                priority=len(path))

    def createEnviron(self):
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

    def _on_request(self, event, request, response):
        if self.path and not request.path.startswith(self.path):
            return

        req = event
        path = request.path

        if self.path is not None:
            path = path[len(self.path):]
            req.path = path

        self._request = request
        self._response = response

        try:
            return self.app(self.createEnviron(), self.start_response)
        except Exception, error:
            status = 500
            message = str(error)
            error = _exc_info()
            etype, evalue, etraceback = _exc_info()
            error = (etype, evalue, format_tb(etraceback))
            return HTTPError(request, response, status, message, error)
