#!/usr/bin/env python

from circuits import Component
from circuits.tools import graph


class Pound(Component):

    def __init__(self):
        super(Pound, self).__init__()

        self.bob = Bob().register(self)
        self.fred = Fred().register(self)

    def started(self, *args):
        print(graph(self.root))


class Bob(Component):

    def started(self, *args):
        print("Hello I'm Bob!")


class Fred(Component):

    def started(self, *args):
        print("Hello I'm Fred!")

Pound().run()
