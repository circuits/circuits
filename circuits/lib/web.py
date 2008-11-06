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

from inspect import getargspec

from circuits import Component
from circuits.lib.sockets import TCPServer
from circuits.lib.http import HTTP, Dispatcher

def expose(*args, **kwargs):
	def decorate(f):
		def wrapper(self, request, listener, *args_, **kwargs_):
			self.request = request
			self.listener = listener
			ret = f(self, *args_, **kwargs_)
			del self.request
			del self.listener
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

class AutoListener(type):

	def __init__(cls, name, bases, dct):
		for name, func in dct.iteritems():
			if callable(func) and not name.startswith("__"):
				setattr(cls, name, expose(name, type="listener")(func))

class Controller(Component):

	__metaclass__ = AutoListener

	channel = "/"
	request = None
