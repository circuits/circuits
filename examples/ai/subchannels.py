#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from circuits import listener, Event, Component, Manager

class Foo(Component):

	__channelPrefix__ = "foo"

	@listener("test")
	def onTEST(self, s):
		print "Hello %s" % s

class Bar(Component):

	__channelPrefix__ = "bar"

	@listener("test")
	def onTEST(self, s):
		print "Hello %s" % s

def main():
	e = Manager()

	foo = Foo(e)
	bar = Bar(e)

	e.send(Event("hello from Foo"), "foo:test", foo)
	e.send(Event("hello from Bar"), "bar:test", bar)

if __name__ == "__main__":
	main()
