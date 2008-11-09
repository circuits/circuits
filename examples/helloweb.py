#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Web Hello

A simple example web server/application displaying "Hello World"
to the user's browser. This example demonstrates how to build a
simple but complete web server and application using circuits.
"""

from circuits.lib.sockets import TCPServer
from circuits import __version__ as systemVersion
from circuits.lib.http import HTTP, Response, Dispatcher
from circuits import listener, Event, Component, Manager

class HelloWorld(Component):
	"""HelloWorld Component

	A Component that will istener to "index' Events and return an appropiate
	HTTP Response with the message "Hello Worl!".
	"""

	# Set channel to "/" which maps to http://localhost:8000/

	channel = "/"

	@listener("index")
	def onINDEX(self, request, response, *args, **kwargs):
		"""Index Event Handler

		HTTP Request Handler that listens on the "index' channel which maps
		to http://localhost:8000/ When a Request is received, send back an
		appropiate HTTP Response with contens of the body being "Hello World!"
		"""

		response.body = "Hello World!"
		self.send(Response(response), "response")

class WebServer(TCPServer):
	"""Web Server Component

	A bsic Web Server Component that combines the HTTP and Dispatcher
	Components into one. Other Components that are added/registered
	to teh system can listen for Events that are matched and mapped
	according to the requested path. For example, http://localhost:8000/foo
	will map to a Component that listens on the "/" channel and contains an
	Event handler that listens on the "foo" channel.
	"""

	def __init__(self, *args, **kwargs):
		"""Initialize Web Server Component

		Create instances of the HTTP and TCPServer Components and add them
		to our Web Server Component.
		"""

		# Important: Call the super constructors to initialize the Component.
		super(WebServer, self).__init__(*args, **kwargs)

		self.http = HTTP()
		self.dispatcher = Dispatcher()
		self += self.http
		self += self.dispatcher

	def run(self):
		while True:
			try:
				self.flush()
				self.poll()
			except KeyboardInterrupt:
				break

if __name__ == "__main__":
	server = WebServer(8000)
	server += HelloWorld()
	server.run()
