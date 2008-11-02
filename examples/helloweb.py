#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Web Hello

Web-based Hello World example.
"""

import optparse

from circuits.lib.sockets import TCPServer
from circuits import __version__ as systemVersion
from circuits.lib.http import HTTP, Response, Dispatcher
from circuits import listener, Event, Component, Debugger, Manager

USAGE = "%prog [options] [path]"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-b", "--bind",
			action="store", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:port")

	opts, args = parser.parse_args()

	return opts, args

###
### Components
###

class HelloWorld(Component):

	channel = "/"

	@listener("index")
	def onINDEX(self, request, response):
		response.body = "Hello World!"
		self.send(Response(response), "response")

class WebServer(TCPServer):

	def registered(self):
		self.manager += HTTP()
		self.manager += Dispatcher()

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 80

	manager = Manager()
	debugger = Debugger()
	server = WebServer(port, address)

	debugger.enable()
	#debugger.IgnoreEvents.extend(["Read", "Write", "Send", "Close"])

	manager += server
	manager += debugger
	manager += HelloWorld()

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
