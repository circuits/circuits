#!/usr/bin/env python

from circuits import Component


class Bob(Component):

    def started(self, *args):
        print("Hello I'm Bob!")


class Fred(Component):

    def started(self, *args):
        print("Hello I'm Fred!")

(Bob() + Fred()).run()
