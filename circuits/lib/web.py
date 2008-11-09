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
		def wrapper(self, request, response, *args, **kwargs):
			self.request, self.response = request, response
			self.cookie = self.request.cookie
			ret = f(self, *args, **kwargs)
			del self.cookie
			del self.request
			del self.response
			return ret
 
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

class Server(TCPServer):

	_docroot = os.getcwd()

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.http = HTTP()
		self.dispatcher = Dispatcher()
		self.dispatcher.docroot = self.docroot

		self.manager += self.http
		self.manager += self.dispatcher

		if self.address in ["", "0.0.0.0"]:
			bound = "%s:%s" % (gethostname(), self.port)
		else:
			bound = "%s:%s" % (self.address, self.port)

		print "%s listening on http://%s/" % (SERVER_VERSION, bound)

	def _getDocRoot(self):
		return self._docroot

	def _setDocRoot(self, docroot):
		if os.path.exists(docroot):
			self._docroot = docroot
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

class Logger(Component):

	channel = "*"

	@listener("request", type="filter")
	def onGET(self, request, response):
		print request

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
				env("QUERY_STRING"),
				headers)

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

		self.send(Response(response), "response")

	@listener("response")
	def onRESPONSE(self, response):
		for k, v in response.cookie.iteritems():
			response.headers.add_header("Set-Cookie", v.OutputString())
		response.start_response(response.status, response.headers.items())

	def __call__(self, environ, start_response):
		request, response = self.getRequestResponse(environ)
		response.start_response = start_response

		try:
			self.send(Request(request, response), "request")
		except HTTPRedirect, error:
			error.set_response()
			self.send(Response(response), "response")
		except HTTPError, error:
			self.setError(response, error[0], error[1])
		except Exception, error:
			self.setError(response, 500, "Internal Server Error", format_exc())
		finally:
			return [response.body]

class _AutoListener(type):

	def __init__(cls, name, bases, dct):
		for name, func in dct.iteritems():
			if callable(func) and not name.startswith("__"):
				setattr(cls, name, expose(name, type="listener")(func))

class Controller(Component):

	__metaclass__ = _AutoListener

	channel = "/"
	request = None

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
			return self.send(Response(response), "response")

		data = {}
		data["path"] = path or "/"

		files = []

		if path:
			href = os.path.join(self.channel, path.lstrip("/"), "..")
			files.append("<li class=\"dir\"><a href=\"%s\">..</a>" % href)

		for file in listdir(real):
			href = os.path.join(self.channel, path.lstrip("/"), file)
			name = ("%s/" % file if isdir(file) else file)
			files.append("<li class=\"dir\"><a href=\"%s\">%s</a>" % (href, name))

		data["files"] = "<ul>%s</ul>" % "".join(files)

		response.body = self.template % data
		self.send(Response(response), "response")
