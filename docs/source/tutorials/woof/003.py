#!/usr/bin/env python

from circuits import Component


class MyComponent(Component):

    def started(self, *args):
        print("Hello World!")

MyComponent().run()
