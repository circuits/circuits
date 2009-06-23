#!/usr/bin/python -i

from circuits import Event, Component

class Foo(Event):
    success = "foo_success"
    failure = "foo_failure"

class System(Component):

    def foo(self):
        return "foo"

    def foo_success(self, r):
        print "foo: %s" % repr(r)

    def foo_failure(self, e):
        print "foo: %s" % str(e)

sys = System()
sys.start()
