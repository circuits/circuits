#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) IRC Bot

A simple example of using circuits to build a simple IRC Bot.

This example demonstrates:
	* Basic Component creation.
	* Basic Event handling.
	* Basic Networking

This example makes use of:
	* Component
	* Event
	* Manager
	* lib.sockets.TCPClient
"""

import optparse
from time import sleep
from socket import gethostname

from circuits.lib.irc import IRC
from circuits.lib.sockets import TCPClient
from circuits import __version__ as systemVersion
from circuits import listener, Event, Component, Debugger, Manager

USAGE = "%prog [options] host [port]"
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

	parser.add_option("-s", "--ssl",
			action="store_true", default=False, dest="ssl",
			help="Enable SSL mode")

	parser.add_option("-d", "--debug",
			action="store_true", default=False, dest="debug",
			help="Enable debug mode")

	opts, args = parser.parse_args()

	if len(args) < 1:
		parser.print_help()
		raise SystemExit, 1

	return opts, args

###
### Components
###

class Bot(Component):

	def __init__(self, *args, **kwargs):
		self.irc = IRC()
		self.client = TCPClient()

	def registered(self):
		self.manager += self.irc
		self.manager += self.client

	def connect(self, host, port, ssl=False):
		self.client.open(host, port, ssl)

	@listener("connect")
	def onCONNECT(self, host, port):
		self.irc.ircUSER("test", gethostname(), host, "Test Bot")
		self.irc.ircNICK("test")

	@listener("numeric")
	def onNUMERIC(self, source, target, numeric, args, message):
		if numeric == 433:
			self.irc.ircNICK("%s_" % self.irc.getNick())

	def run(self):
		while self.client.connected:
			try:
				self.manager.flush()
				self.client.poll()
				sleep(0.01)
			except KeyboardInterrupt:
				self.irc.ircQUIT()
				self.manager.flush()

###
### Main
###

def main():
	opts, args = parse_options()

	if ":" in args[0]:
		host, port = args[0].split(":")
		port = int(port)
	else:
		host = args[0]
		port = 6667

	manager = Manager()

	if opts.debug:
		debugger = Debugger()
		manager += debugger
		debugger.IgnoreEvents = ["Read", "Write", "Raw"]

	bot = Bot()
	manager += bot

	bot.connect(host, port, opts.ssl)
	bot.run()

###
### Entry Point
###

if __name__ == "__main__":
	main()
