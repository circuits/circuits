#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) IRC Bot

A simple example of using circuits to build a simple IRC Bot.
This example demonstrates basic networking with circuits.
"""

from time import sleep
from socket import gethostname

from circuits.lib.irc import IRC
from circuits import listener, Component
from circuits.lib.sockets import TCPClient

class Bot(Component):

	def __init__(self, *args, **kwargs):
		"""Initialize Bot Component

		Create instances of the IRC and TCPClient Components and add them
		to our Bot Component.
		"""

		# Important: Call the super constructors to initialize the Component.
		super(Bot, self).__init__(*args, **kwargs)

		self.irc = IRC()
		self.client = TCPClient()
		self += self.irc
		self += self.client

	def connect(self, host, port=6667, ssl=False):
		"Connect to an IRC Server"

		self.client.open(host, port, ssl)

	@listener("connect")
	def onCONNECT(self, host, port):
		"""Connect Event Handler

		Event Handler for "connect" Events that implements:
		 * When the Bot has connectd:
		  * Send a USER command
		  * Send a NICK command
		"""

		self.irc.ircUSER("test", gethostname(), host, "Test Bot")
		self.irc.ircNICK("test")

	@listener("numeric")
	def onNUMERIC(self, source, target, numeric, args, message):
		"""Numeric Event Handler

		Event Handler for "numeric" Events that implements:
		 * When the Bot receives a numeric message:
		  * If the numeric is a 433:
		   * Change our nick by appending a "_" to our current nick

		Note: 433 is the IRC numeric for "Nickname in use"
		"""

		if numeric == 433:
			self.irc.ircNICK("%s_" % self.irc.getNick())

	@listener("message")
	def onMESSAGE(self, source, target, message):
		"""Message Event Handler

		Event Handler for "message" Events that implements:
		 * When the Bot receives a message:
		  * Echo the message back to the sender (source).
		"""

		self.irc.ircPRIVMSG(source, message)

	def run(self):
		"""Run the Bot

		Main Event Loop that runs the Bot. This flushes all Events waiting
		to be processed, then polls for new Events from the TCPClient
		Component. If a ^C is issued, send a QUIT command and flush any
		remaining Events and terminate. Continue running whiel the TCPClient
		is still connected to the Server.
		"""

		while self.client.connected:
			try:
				self.flush()
				self.client.poll()
				sleep(0.01)
			except KeyboardInterrupt:
				self.irc.ircQUIT()
				self.flush()

if __name__ == "__main__":
	bot = Bot()
	bot.connect("irc.freenode.net")
	bot.run()
