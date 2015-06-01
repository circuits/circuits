#!/usr/bin/env python

"""circuits Hello World"""

from circuits import Component, Event


class hello(Event):

    """hello Event"""


class App(Component):

    def hello(self):
        """Hello Event Handler"""

        print("Hello World!")

    def started(self, component):
        """Started Event Handler

        This is fired internally when your application starts up and can be used to
        trigger events that only occur once during startup.
        """

        self.fire(hello())  # Fire hello Event

        raise SystemExit(0)  # Terminate the Application

App().run()
