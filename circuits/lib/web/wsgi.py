# Module:   wsgi
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WSGI Components

This module implements WSGI Components.
"""

from traceback import format_exc

from circuits import handler, Component

import webob
from headers import Headers
from errors import HTTPError
from utils import quoteHTML, url
from dispatchers import Dispatcher
from events import Request, Response
from constants import RESPONSES, DEFAULT_ERROR_MESSAGE, SERVER_VERSION

class Application(Component):

    headerNames = {
            "HTTP_CGI_AUTHORIZATION": "Authorization",
            "CONTENT_LENGTH": "Content-Length",
            "CONTENT_TYPE": "Content-Type",
            "REMOTE_HOST": "Remote-Host",
            "REMOTE_ADDR": "Remote-Addr",
            }

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        Dispatcher(**kwargs).register(self)

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
        request = webob.Request(None,
                env("REQUEST_METHOD"),
                env("wsgi.url_scheme"),
                env("PATH_INFO"),
                protocol,
                env("QUERY_STRING"))

        request.remote = webob.Host(env("REMOTE_ADDR"), env("REMTOE_PORT"))

        request.headers = headers
        request.script_name = env("SCRIPT_NAME")
        request.wsgi_environ = environ
        request.body = env("wsgi.input")

        response = webob.Response(None, request)
        response.headers.add_header("X-Powered-By", SERVER_VERSION)
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
        response.headers.add_header("Connection", "close")

    def __call__(self, environ, start_response):
        request, response = self.getRequestResponse(environ)

        try:
            self.send(Request(request, response), "request", self.channel)
        except:
            error = HTTPError(request, response, 500, error=format_exc())
            self.send(error, "httperror", self.channel)
        finally:
            body = response.process()
            start_response(response.status, response.headers.items())
            return [body]

class Middleware(Component):

    def __init__(self, app, path=None):
        super(Middleware, self).__init__(channel=path)

        self.app = app
        self.request = self.response = None

    def environ(self):
        environ = {}
        req = self.request
        env = environ.__setitem__

        env("REQUEST_METHOD", req.method)
        env("PATH_INFO", req.path)
        env("SERVER_PROTOCOL", req.server_protocol)
        env("QUERY_STRING", req.qs)
        env("SCRIPT_NAME", req.script_name)
        env("wsgi.input", req.body)

        return environ

    def start_response(self, status, headers):
        self.response.stats = status
        for header in headers:
            self.response.headers.add_header(*header)

    @handler("request", filter=True)
    def onREQUEST(self, request, response, *args, **kwargs):
        self.request = request
        self.response = response

        return "".join(self.app(self.environ(), self.start_response))

class Filter(Component):

    @handler("response", filter=True)
    def onRESPONSE(self, request, response):
        self.request = request
        self.response = response

        try:
            response.body = self.process()
        finally:
            del self.request
            del self.response
