# Module:   test_utils
# Date:     ...
# Author:   ...

"""test_utils

...
"""


from circuits import Event


class Test(Event):
    """Test Event"""


def test():
    from circuits.node.utils import dump_event, load_event

    e = Test(1, 2, 3, foo="bar")
    e.success = True
    e.failure = False

    s = dump_event(e)
    x = load_event(s)

    assert e == x
    assert hasattr(x, "args")
    assert hasattr(x, "kwargs")
    assert hasattr(x, "success")
    assert hasattr(x, "failure")
    assert hasattr(x, "channels")
