#!/usr/bin/python -i

from circuits import handler, Event, Component, Manager, Debugger

class Changed(Event):
    """Changed(Event): -> new Changed Event

    args:
        old, new

    Note:
        The value component itself (self) is always passed as the first
        argument to identify the value that has changed.
    """

class Deleted(Event): pass

class Value(Component):

    def __init__(self, value):
        self.__value = value
        super(Value, self).__init__()

    def __repr__(self):
        return "<Value(%r)>" % self.__value

    def __set__(self, instance, value):
        if not self.manager == instance:
            self.register(instance)
        oldvalue = self.__value
        self.__value = value
        self.push(Changed(self, oldvalue, value), "changed", self.channel)

    def __delete__(self, instance):
        oldvalue = self.__value
        self.push(Deleted(self, oldvalue), "changed", self.channel)
        self.unregister()

class Foo(Component):

    x = Value(1)

m = Manager() + Debugger()
foo = Foo()
m += foo
m.start()
