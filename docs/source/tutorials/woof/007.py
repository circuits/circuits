#!/usr/bin/env python

from circuits import Component, Event


class woof(Event):
    """woof Event."""


class Pound(Component):
    def __init__(self) -> None:
        super().__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)

    def started(self, *args) -> None:
        self.fire(woof(), self.bob)


class Dog(Component):
    def woof(self) -> None:
        print("Woof! I'm %s!" % self.name)


class Bob(Dog):
    """Bob."""

    channel = 'bob'


class Fred(Dog):
    """Fred."""

    channel = 'fred'


Pound().run()
