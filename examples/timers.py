#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Timers

A trivial simple example of using circuits and timers.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.
    * Use of Timer Component

This example makes use of:
    * Component
    * Event
    * Manager
    * timers.Timer
"""

from circuits import Timer
from circuits.core import Event, Component, Manager

###
### Components
###

class HelloWorld(Component):

    def hello(self):
        print "Hello World"

    def foo(self):
        print "Foo"

    def bar(self):
        print "Bar"

###
### Main
###

def main():
    manager = Manager() + HelloWorld()

    manager += Timer(5, Event(), "hello")
    manager += Timer(1, Event(), "foo", persist=True)
    manager += Timer(3, Event(), "bar", persist=True)

    manager.run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
