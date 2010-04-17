# Module:   test_event_serialization
# Date:     13th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Event Serialization Tests"""

from time import sleep
from pickle import dumps, loads

from circuits import Event, Component

class Test(Event):
    """Test Event"""

    success = ("test_successful",)

class App(Component):

    def test(self):
        return "Hello World!"

def test():
    app = App()
    while app: app.flush()

    e = Test()
    app.push(e)
    app.flush()

    s = dumps(e, -1)
    x = loads(s)

    assert e == x
