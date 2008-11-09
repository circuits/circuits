#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Timers

A trivial simple example of using circuits and timers.

This example demonstrates:
	* Basic Component creation.
	* Basic Event handling.
	* Use of Timer Component

This example makes use of:
	* Component
	* Event
	* Manager
	* timers.Timer
"""

from circuits import Timer
from circuits.core import listener, Event, Component, Manager

###
### Components
###

class HelloWorld(Component):

	@listener("hello")
	def onHELLO(self):
		print "Hello World"

	@listener("foo")
	def onFOO(self):
		print "Foo"

	@listener("bar")
	def onBAR(self):
		print "Bar"

###
### Main
###

def main():
	manager = Manager()
	manager += HelloWorld()

	timers = []

	timers.append(Timer(5, Event("Hello"), "hello"))
	timers.append(Timer(1, Event("Foo"), "foo", persist=True))
	timers.append(Timer(3, Event("Bar"), "bar", persist=True))

	for timer in timers:
		manager += timer

	while True:
		try:
			manager.flush()
			for timer in timers[:]:
				if timer.manager == manager:
					timer.poll()
				else:
					timers.remove(timer)
		except KeyboardInterrupt:
			break

###
### Entry Point
###

if __name__ == "__main__":
	main()
