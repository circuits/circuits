#!/usr/bin/env python
"""
circuits Signal Handling.

A modified version of the circuits Hello World example to demonstrate
how to customize signal handling and cause a delayed system terminate.
"""

from circuits import Component, Debugger, Event, Timer


class hello(Event):
    """hello Event."""


class App(Component):
    def hello(self) -> None:
        """Hello Event Handler."""
        print('Hello World!')

    def signal(self, event, signo, stack) -> None:
        Timer(3, Event.create('terminate')).register(self)
        print('Terminating in 3 seconds...')

    def terminate(self) -> None:
        self.stop()

    def started(self, component) -> None:
        """
        Started Event Handler.

        This is fired internally when your application starts up
        and can be used to trigger events that only occur once
        during startup.
        """
        self.fire(hello())  # Fire hello Event


(App() + Debugger()).run()
