#!/usr/bin/env python
"""Simple Event Filtering

This example shows how you can filter events by using the ``Event.stop()``
method which prevents other event handlers listening to the event from
running. When this example is run you should only get a single line of
output "Hello World!".

.. code-block:: sh

    $ ./filter.py
    Hello World!
"""
from __future__ import print_function

from circuits import Component, Event


class hello(Event):

    """hello Event"""


class App(Component):

    def hello(self, event):
        """Hello Event Handler"""

        event.stop()  # Stop further event processing

        print("Hello World!")

    def started(self, event, component):
        """Started Event Handler

        This is fired internally when your application starts up
        and can be used to trigger events that only occur once
        during startup.
        """

        event.stop()  # Stop further event processing
        self.fire(hello())  # Fire a Hello event
        raise SystemExit(0)  # Terminate the application


# Start and "run" the system.
# We're deliberately creating two instances of ``App``
# so we can demonstrate event filtering.
app = App()
App().register(app)  # 2nd App
app.run()
