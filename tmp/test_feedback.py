#!/usr/bin/python -i

from circuits import Event, Component, Debugger

class Foo(Event):
    success = "foo_success"
    failure = "foo_failure"

class System(Component):

    def foo(self):
        return "foo"

    def foo_success(self, evt, handler, retval):
        print "%s successfully executed by %s with return value %s" % (
                evt, handler, repr(retval))

    def foo_failure(self, evt, handler, error):
        print "%s failed execution by %s with error %s" % (
                evt, handler, error)

sys = System()# + Debugger()
sys.start()
