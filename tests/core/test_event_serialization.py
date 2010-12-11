# Module:   test_event_serialization
# Date:     13th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Event Serialization Tests"""

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
    assert hasattr(x, "args")
    assert hasattr(x, "kwargs")
    assert hasattr(x, "channel")
    assert hasattr(x, "target")
    assert hasattr(x, "success")
    assert hasattr(x, "failure")
    assert hasattr(x, "filter")
    assert hasattr(x, "start")
    assert hasattr(x, "end")
    assert hasattr(x, "value")
    assert hasattr(x, "source")
