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

import sys
from inspect import getargspec

from circuits import listener, Component
from circuits.lib.sockets import TCPServer
from circuits.lib.http import HTTP, Dispatcher
from circuits.lib.http import Request, Response, _Request, _Response, Headers

def expose(*args, **kwargs):
	def decorate(f):
		def wrapper(self, request, response, *args_, **kwargs_):
			self.request = request
			self.response = response
			ret = f(self, *args_, **kwargs_)
			del self.request
			del self.response
			return ret
 
		wrapper.type = kwargs.get("type", "listener")
		wrapper.target = kwargs.get("target", None)
		wrapper.channels = args
		wrapper.argspec = getargspec(f)
		wrapper.args = wrapper.argspec[0][1:]
		wrapper.varargs = (True if wrapper.argspec[1] else False)
		wrapper.varkw = (True if wrapper.argspec[2] else False)
		return wrapper

	return decorate

class Server(TCPServer):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.manager += HTTP()
		self.manager += Dispatcher()

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
				env("QUERY_STRING"),
				headers)

		request.script_name = env("SCRIPT_NAME")
		request.wsgi_environ = environ

		request.body = env("wsgi.input")
		response = _Response(None)

		response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

		return request, response

	@listener("response")
	def onRESPONSE(self, response):
		response.start_response(response.status, response.headers.items())

	def __call__(self, environ, start_response):
		request, response = self.getRequestResponse(environ)
		response.start_response = start_response
		self.send(Request(request, response), "request")
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
