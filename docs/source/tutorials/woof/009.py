#!/usr/bin/env python

from circuits import Component, Event


class bark(Event):
    """bark Event."""


class Pound(Component):
    def __init__(self) -> None:
        super().__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)


class Dog(Component):
    def started(self, *args) -> None:
        self.fire(bark())

    def bark(self) -> None:
        print("Woof! I'm %s!" % name)  # noqa


class Bob(Dog):
    """Bob."""

    channel = 'bob'


class Fred(Dog):
    """Fred."""

    channel = 'fred'


Pound().run()
