#!/usr/bin/env python
"""Simple Timers

A trivial simple example of using circuits and timers.
"""
from circuits import Component, Event, Timer


class App(Component):

    def hello(self):
        """hello Event handler

        Fired once in 5 seconds.
        """

        print("Hello World")

    def foo(self):
        """foo Event handler

        Fired every 1 seconds.
        """

        print("Foo")

    def bar(self):
        """bar Event handler

        Fired every 3 seconds.
        """

        print("Bar")

    def started(self, component):
        """started Event handler

        Setup 3 timers at 5, 1 and 3 seconds.
        The 2nd two timers are persitent meaning that
        they are fired repeatedly every 1 and 3 seconds
        respectively.
        """

        # Timer(seconds, event, persist=False)
        Timer(5, Event.create("hello")).register(self)
        Timer(1, Event.create("foo"), persist=True).register(self)
        Timer(3, Event.create("bar"), persist=True).register(self)


App().run()
