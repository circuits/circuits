#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Hello World

A trivial simple example of using circuits to print a simple
message.

This example demonstrates:
	* Basic Component creation.
	* Basic Event handling.

This example makes use of:
	* Component
	* Event
	* Manager
"""

from circuits.core import listener, Event, Component, Manager

###
### Events
###

class Message(Event):
	"""Message(Event) -> Message Event

	args: message
	"""

###
### Components
###

class Printer(Component):

	@listener("print")
	def onPRINT(self, message=""):
		print message

###
### Main
###

def main():
	manager = Manager()
	manager += Printer()

	manager.push(Message("Hello World"), "print")
	manager.flush()

###
### Entry Point
###

if __name__ == "__main__":
	main()
