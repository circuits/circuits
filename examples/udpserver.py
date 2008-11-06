#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Simple UDP Server

A trivial simple example of using circuits to build a simple
UDP Socket Server.

This example demonstrates:
	* Basic Component creation.
	* Basic Event handling.
	* Basic Networking

This example makes use of:
	* Component
	* Event
	* Manager
	* lib.sockets.UDPServer
"""

from circuits.lib.sockets import UDPServer
from circuits.core import listener, Event, Component, Manager

class EchoServer(UDPServer):

	@listener("read")
	def onREAD(self, address, data):
		print "%s, %s:" % address
		print data.strip()
		self.write(address, data.strip())
	
def main():
	manager = Manager()
	server = EchoServer(8000)
	manager += server

	while True:
		try:
			manager.flush()
			server.poll()
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()
