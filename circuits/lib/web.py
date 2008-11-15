# Module:	web
# Date:		6th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Web Components

This module implements Web Components that can be used to build
web applications and web systems, be it an AJAX backend, a RESTful
server or a website. These components offer a full featured web
server implementation with support for headers, cookies, positional
and keyword arguments, filtering, url dispatching and more.
"""

import os
import sys
import rfc822
import datetime
from os import getcwd, listdir
from inspect import getargspec
from socket import gethostname
from os.path import isdir, isfile

from circuits import listener, Component
from circuits.lib.sockets import TCPServer
from circuits.lib.http import HTTPError, HTTPRedirect
from circuits.lib.http import RESPONSES, DEFAULT_ERROR_MESSAGE
from circuits.lib.http import SERVER_VERSION, HTTP, Dispatcher
from circuits.lib.http import Request, Response, _Request, _Response, Headers

def expose(*channels, **config):
	def decorate(f):
		def wrapper(self, *args, **kwargs):
			if not hasattr(self, "request"):
				self.request, self.response = args[:2]
				self.cookie = self.request.cookie
				args = args[2:]

			try:
				return f(self, *args, **kwargs)
			finally:
				if hasattr(self, "request"):
					del self.request
					del self.response
					del self.cookie
 
		wrapper.type = config.get("type", "listener")
		wrapper.target = config.get("target", None)
		wrapper.channels = channels
		wrapper.argspec = getargspec(f)
		wrapper.args = wrapper.argspec[0][1:]
		wrapper.args.insert(0, "response")
		wrapper.args.insert(0, "request")
		wrapper.varargs = (True if wrapper.argspec[1] else False)
		wrapper.varkw = (True if wrapper.argspec[2] else False)
		return wrapper

	return decorate

class _AutoListener(type):

	def __init__(cls, name, bases, dct):
		for name, func in dct.iteritems():
			if callable(func) and not name.startswith("_"):
				setattr(cls, name, expose(name, type="listener")(func))

class Server(TCPServer):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.http = HTTP()
		self.dispatcher = Dispatcher()

		self.manager += self.http
		self.manager += self.dispatcher

		if self.address in ["", "0.0.0.0"]:
			bound = "%s:%s" % (gethostname(), self.port)
		else:
			bound = "%s:%s" % (self.address, self.port)

		print "%s listening on http://%s/" % (SERVER_VERSION, bound)

	def _getDocRoot(self):
		if hasattr(self, "dispatcher"):
			return self.dispatcher.docroot
		else:
			return None

	def _setDocRoot(self, docroot):
		if os.path.exists(docroot):
			self.dispatcher.docroot = docroot
		else:
			raise IOError(2, "Invalid docroot path", docroot)

	docroot = property(_getDocRoot, _setDocRoot, "Document Root")

	def run(self):
		while True:
			try:
				self.flush()
				self.poll()
			except KeyboardInterrupt:
				break

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

	def _setError(self, response, code, message=None, traceback=None):
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
		request, response = self._getRequestResponse(environ)

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

		self.send(Response(request, response), "response")

class Filter(Component):

	@listener("response", type="filter")
	def onRESPONSE(self, request, response):
		self.request = request
		self.response = response

		print request
		print response

		try:
			print self.process()
			response.body = self.process()
		finally:
			del self.request
			del self.response

class Controller(Component):

	__metaclass__ = _AutoListener

	channel = "/"

class Logger(Component):

	format = "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\""

	@listener("request")
	def onREQUEST(self, request, response):
		self.log(request, response)

	def log(self, request, response):
		remote = request.remote_host
		outheaders = response.headers
		inheaders = request.headers
		
		atoms = {"h": remote.name or remote.ip,
				 "l": "-",
				 "u": getattr(request, "login", None) or "-",
				 "t": self.time(),
				 "r": request.request_line,
				 "s": response.status.split(" ", 1)[0],
				 "b": outheaders.get("Content-Length", "") or "-",
				 "f": inheaders.get("Referer", ""),
				 "a": inheaders.get("User-Agent", ""),
				 }
		for k, v in atoms.items():
			if isinstance(v, unicode):
				v = v.encode("utf8")
			elif not isinstance(v, str):
				v = str(v)
			# Fortunately, repr(str) escapes unprintable chars, \n, \t, etc
			# and backslash for us. All we have to do is strip the quotes.
			v = repr(v)[1:-1]
			# Escape double-quote.
			atoms[k] = v.replace("\"", "\\\"")
		
		print >> sys.stderr, self.format % atoms
	
	def time(self):
		now = datetime.datetime.now()
		month = rfc822._monthnames[now.month - 1].capitalize()
		return ("[%02d/%s/%04d:%02d:%02d:%02d]" %
				(now.day, month, now.year, now.hour, now.minute, now.second))
	
class FileServer(Component):

	template = """\
<html>
 <head>
  <title>Index of %(path)s</title>
 </head>
 <body>
  <h1>Index of %(path)s</h1>
%(files)s
 </body>
</html>"""

	def __init__(self, *args, **kwargs):
		super(FileServer, self).__init__(*args, **kwargs)

		self.path = kwargs.get("path", getcwd())

	@listener("index")
	def onINDEX(self, request, response, *args, **kwargs):
		if args:
			path = os.path.join("/", *args)
			real = os.path.join(self.path, *args)
		else:
			path = ""
			real = self.path

		if isfile(real):
			response.body = open(real, "r")
			return self.send(Response(request, response), "response")

		data = {}
		data["path"] = path or "/"

		files = []

		if path:
			href = os.path.join(self.channel, path.lstrip("/"), "..")
			files.append("<li class=\"dir\"><a href=\"%s\">..</a>" % href)

		for file in listdir(real):
			href = os.path.join(self.channel, path.lstrip("/"), file)
			name = ("%s/" % file if isdir(file) else file)
			files.append("   <li class=\"dir\"><a href=\"%s\">%s</a>" % (
				href, name))

		data["files"] = "  <ul>\n%s\n  </ul>" % "\n".join(files)

		response.headers["Content-Type"] = "text/html"
		response.body = self.template % data
		self.send(Response(request, response), "response")
