#!/usr/bin/env python
"""circuits Hello World"""

from __future__ import print_function

from circuits import Component, Event


class hello(Event):
    """hello Event"""


class terminate(Event):
    """terminate Event"""


class App(Component):

    def hello(self):
        """Hello Event Handler"""

        print("Hello World!")

    def started(self, *args):
        """Started Event Handler

        This is fired internally when your application starts up
        and can be used to trigger events that only occur once
        during startup.
        """

        self.fire(hello())  # Fire hello Event
        self.fire(terminate())

    def terminate(self):
        raise SystemExit(0)  # Terminate the Application


App().run()
