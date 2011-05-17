#!/usr/bin/env python

from circuits import Component, Event


class Test(Component):

    def foo(self):
        print "Foobar!"

test = Test()
test.start()
