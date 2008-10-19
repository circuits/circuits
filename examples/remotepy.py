#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Remote Python

An example of using circuits and the event bdirge to create a server/client
system capable of executing remote python. In client mode, the user inputs
some arbitary python expression which is packaged up and sent as a remote
event across the event bridge to the server. The server processes and
computes the expression, packages up the result and sends it back across
the event bridge as an event.

This example demonstrates:
	* Basic Request/Response model using events.
	* Briding systems/components.

This example makes use of:
	* Component
	* Bridge
	* Manager
	* Stdin (lib)
"""

import sys
import optparse

import circuits
from circuits import Debugger
from circuits import listener, Event, Component, Bridge, Manager
from circuits.lib.io import Stdin

USAGE = "%prog [options] [host[:port]]"
VERSION = "%prog v" + circuits.__version__

ERRORS = {}
ERRORS[0] = "Specify either server (-s/--server) mode or client (-c/--client mode"
ERRORS[1] = "Only specify one of either server (-s/--server) mode or client (-c/--client mode"

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse the command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-s", "--server",
			action="store_true", default=False, dest="server",
			help="Server mode")

	parser.add_option("-c", "--client",
			action="store_true", default=False, dest="client",
			help="Client mode")

	parser.add_option("-b", "--bind",
			action="store", type="string", default="0.0.0.0:8000", dest="bind",
			help="Bind to address:port")

	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode")

	opts, args = parser.parse_args()

	if not (opts.server or opts.client):
		print "ERROR: %s" % ERRORS[0]
		parser.print_help()
		raise SystemExit, 1
	elif opts.server and opts.client:
		print "ERROR: %s" % ERRORS[1]
		parser.print_help()
		raise SystemExit, 2

	return opts, args

###
### Events
###

class Result(Event): pass
class NewInput(Event): pass

###
### Components
###

class Input(Stdin):

	@listener("read")
	def onREAD(self, data):
		self.push(NewInput(data.strip()), "newinput")

class Calc(Component):

	@listener("result")
	def onRESULT(self, r):
		sys.stdout.write("%s\n" % r)
		sys.stdout.write(">>> ")
		sys.stdout.flush()

class Adder(Component):

	@listener("newinput")
	def onNEWINPUT(self, s):
		print "Evaluating: %s" % s
		r = eval(s)
		self.push(Result(r), "result")

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in opts.bind:
		address, port = opts.bind.split(":")
		port = int(port)
	else:
		address, port = opts.bind, 8000

	if args:
		x = args[0].split(":")
		if len(x) > 1:
			nodes = [(x[0], int(x[1]))]
		else:
			nodes = [(x[0], 8000)]
	else:
		nodes = []

	manager = Manager()

	bridge = Bridge(port, address=address, nodes=nodes)
	manager += bridge

	if opts.debug:
		debugger = Debugger()
		debugger.IgnoreEvents.extend(["Read", "Write"])
		manager += debugger

	if opts.server:
		manager += Adder()

		while True:
			try:
				manager.flush()
				bridge.poll()
			except KeyboardInterrupt:
				break
	elif opts.client:
		input = Input()
		manager += input
		manager += Calc()

		sys.stdout.write(">>> ")
		sys.stdout.flush()

		while True:
			try:
				manager.flush()
				input.poll()
				bridge.poll()
			except KeyboardInterrupt:
				break
	else:
		print "ERROR: Invalid mode"
		raise SystemExit, 255

###
### Entry Point
###

if __name__ == "__main__":
	main()
