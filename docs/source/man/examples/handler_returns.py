#!/usr/bin/env python

from circuits import Component, Debugger, Event


class Identify(Event):

    """Identify Event"""

    success = True


class Pound(Component):

    def __init__(self):
        super(Pound, self).__init__()

        Debugger().register(self)
        Bob().register(self)
        Fred().register(self)

    def started(self, *args):
        self.fire(Identify())

    def Identify_success(self, evt, result):
        if not isinstance(result, list):
            result = [result]
        print "In pound:"
        for name in result:
            print name


class Dog(Component):

    def Identify(self):
        return self.__class__.__name__


class Bob(Dog):

    """Bob"""


class Fred(Dog):

    """Fred"""

Pound().run()
