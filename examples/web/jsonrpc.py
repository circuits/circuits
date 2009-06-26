#!/usr/bin/env python

from circuits import Component
from circuits.web import Server, Logger, JSONRPC

class Test(Component):
	
	def foo(self, a, b, c):
		return a, b, c

(Server(8000) + Logger() + JSONRPC() + Test()).run()
