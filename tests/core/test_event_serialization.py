# Module:   test_event_serialization
# Date:     13th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Event Serialization Tests"""



from circuits import Event

class Test(Event):
    """Test Event"""


def test():
    from circuits.core.events import loads

    e = Test(1, 2, 3, foo="bar")
    e.success = True
    e.failure = False

    s = e.dumps()
    x = loads(s)

    assert e == x
    assert hasattr(x, "args")
    assert hasattr(x, "kwargs")
    assert hasattr(x, "success")
    assert hasattr(x, "failure")
    assert hasattr(x, "channels")
