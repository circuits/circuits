#!/usr/bin/env python
"""circuits Hello World"""

from circuits import Component, Event


class hello(Event):

    """hello Event"""


class App(Component):

    def hello(self):
        """Hello Event Handler"""

        return "Hello World!"

    def started(self, component):
        """Started Event Handler

        This is fired internally when your application starts up and can be used to
        trigger events that only occur once during startup.
        """

        x = self.fire(hello())  # Fire hello Event
        yield self.wait("hello")  # Wait for Hello Event to fire

        print(x.value)  # Print the value we got back from firing Hello

        raise SystemExit(0)  # Terminate the Application


def main():
    App().run()


if __name__ == "__main__":
    main()
