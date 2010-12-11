# Module:   test_value_serialization
# Date:     25th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Value Serialization Tests"""

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

    v = app.push(Test())
    while app: app.flush()

    s = dumps(v, -1)
    x = loads(s)

    assert hasattr(x, "event")
    assert hasattr(x, "onSet")
    assert hasattr(x, "result")
    assert hasattr(x, "errors")
    assert hasattr(x, "_value")

    assert x.event == v.event
    assert x.onSet == v.onSet
    assert x.result == v.result
    assert x.errors == v.errors
    assert x._value == v._value
