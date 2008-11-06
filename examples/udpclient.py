#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) UDP Client

A trivial simple example of using circuits to build a simple
UDP Socket Client.

This example demonstrates:
	* Basic Component creation.
	* Basic Event handling.
	* Basic Networking

This example makes use of:
	* Component
	* Event
	* Manager
	* lib.sockets.UDPClient
"""

import optparse

from circuits.lib.io import Stdin
from circuits.lib.sockets import UDPClient
from circuits import __version__ as systemVersion
from circuits.core import listener, Event, Component, Manager

USAGE = "%prog [options] address:[port]"
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
			action="store", type="str", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:[port]")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

###
### Components
###

class Client(UDPClient):

	def __init__(self, *args, **kwargs):
		super(Client, self).__init__(*args, **kwargs)

		self.dest = kwargs.get("dest", "127.0.0.1:8000")

	@listener("read")
	def onREAD(self, address, data):
		print "%s, %s:" % address
		print data.strip()

	@listener("stdin:read")
	def onINPUT(self, data):
		self.write(self.dest, data)

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts,bind, 8000

	if ":" in args[0]:
		dest = args[0].split(":")
		dest = dest[0], int(dest[1])
	else:
		dest = args[0], 8000

	manager = Manager()

	client = Client(port, address, dest=dest)
	stdin = Stdin()

	manager += stdin
	manager += client

	while True:
		try:
			manager.flush()
			stdin.poll()
			client.poll()
		except KeyboardInterrupt:
			break

	client.close()

###
### Entry Point
###

if __name__ == "__main__":
	main()
