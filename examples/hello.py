#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Hello World

A trivial simple example of using circuits to print a simple
message. This example demonstrates the basics of circutis'
Components and Events and basic Event handling.
"""

from circuits.core import listener, Event, Component, Manager

class Message(Event):
	"""Message Event

	args: message
	"""

class Printer(Component):
	"""Printer Component

	A Component that will listen to "print" Events and print each message
	received.
	"""

	@listener("print")
	def onPRINT(self, message=""):
		"""Print Event Handler

		When a "print" Event has been received, print the message.
		"""

		print message

if __name__ == "__main__":
	# Create new Manager instance
	manager = Manager()

	# Create new Printer instance
	# Add (register) with manager
	manager += Printer()

	# Push a Message Event to the "print" channel.
	manager.push(Message("Hello World"), "print")

	# Process Events
	manager.flush()
