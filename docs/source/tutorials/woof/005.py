#!/usr/bin/env python

from circuits import Component
from circuits.tools import graph


class Pound(Component):
    def __init__(self) -> None:
        super().__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)

    def started(self, *args) -> None:
        print(graph(self.root))


class Bob(Component):
    def started(self, *args) -> None:
        print("Hello I'm Bob!")


class Fred(Component):
    def started(self, *args) -> None:
        print("Hello I'm Fred!")


Pound().run()
