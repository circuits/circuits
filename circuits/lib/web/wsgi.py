# Module:   wsgi
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""WSGI Components

This module implements WSGI Components.
"""

from circuits.core import listener, Component

from dispatchers import Dispatcher

class Application(Component):

   headerNames = {
         "HTTP_CGI_AUTHORIZATION": "Authorization",
         "CONTENT_LENGTH": "Content-Length",
         "CONTENT_TYPE": "Content-Type",
         "REMOTE_HOST": "Remote-Host",
         "REMOTE_ADDR": "Remote-Addr",}

   def __init__(self, *args, **kwargs):
      super(Application, self).__init__(*args, **kwargs)

      self += Dispatcher()

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

      request = _Request(
            env("REQUEST_METHOD"),
            env("PATH_INFO"),
            env("SERVER_PROTOCOL"),
            env("QUERY_STRING"))

      request.headers = headers
      request.script_name = env("SCRIPT_NAME")
      request.wsgi_environ = environ
      request.body = env("wsgi.input")

      response = _Response(None)
      response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

      return request, response

   def setError(self, response, code, message=None, traceback=None):
      try:
         short, long = RESPONSES[code]
      except KeyError:
         short, long = "???", "???"

      if message is None:
         message = short

      explain = long

      content = DEFAULT_ERROR_MESSAGE % {
         "code": code,
         "message": quoteHTML(message),
         "explain": explain,
         "traceback": traceback or ""}

      response.body = content
      response.status = "%s %s" % (code, message)
      response.headers.add_header("Connection", "close")

   def __call__(self, environ, start_response):
      request, response = self.getRequestResponse(environ)

      try:
         self.send(Request(request, response), "request")
      except HTTPRedirect, error:
         error.set_response()
      except HTTPError, error:
         self.setError(response, error[0], error[1])
      except Exception, error:
         self.setError(response, 500, "Internal Server Error", format_exc())
      finally:
         body = response.process()
         start_response(response.status, response.headers.items())
         return [body]

class Middleware(Component):

   request = None
   response = None

   def __init__(self, app, path=None):
      super(Middleware, self).__init__(channel=path)

      self.app = app

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

   @listener("request", type="filter")
   def onREQUEST(self, request, response, *args, **kwargs):
      self.request = request
      self.response = response

      response.body = "".join(self.app(self.environ(), self.start_response))

      self.send(Response(response), "response")

class Filter(Component):

   @listener("response", type="filter")
   def onRESPONSE(self, request, response):
      self.request = request
      self.response = response

      try:
         response.body = self.process()
      finally:
         del self.request
         del self.response
