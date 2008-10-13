#!/usr/bin/env python

from circuits.core import listener, Component, Event, Manager

class Hello(Component):

	@listener("hello")
	def onHELLO(self):
		print "Hello World!"

def main():
	manager = Manager()
	hello = Hello()
	manager += hello

	manager.push(Event(), "hello")
	manager.flush()

if __name__ == "__main__":
	main()
