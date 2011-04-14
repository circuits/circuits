#!/usr/bin/env python

from circuits import Component, Event

class Bark(Event):
    """Bark Event"""

class Pound(Component):

    def __init__(self):
        super(Pound, self).__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)

class Dog(Component):

    def started(self, *args):
        self.fire(Bark())

    def bark(self):
        print("Woof! I'm %s!" % name)

class Bob(Dog):
    """Bob"""

    channel = "bob"

class Fred(Dog):
    """Fred"""

    channel = "fred"

Pound().run()
