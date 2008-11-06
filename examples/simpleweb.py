#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Simple Web Hello

Web-based Hello World example. This example is exactly the same as
the helloweb.py example, except that it tries to simplify things by
using more higher abstracted web components from the web components
library.
"""

from circuits.lib.web import Server
from circuits import listener, Component

class HelloWorld(Component):

	channel = "/"

	@listener("index")
	def onINDEX(self, request, response):
		return "Hello World!"

def main():
	server = Server(8000)
	server += HelloWorld()
	server.run()

if __name__ == "__main__":
	main()
