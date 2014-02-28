# Module:   test_utils
# Date:     ...
# Author:   ...

"""test_utils

...
"""


from circuits import Event


class test(Event):
    """test Event"""


def test_events():
    from circuits.node.utils import dump_event, load_event

    e = test(1, 2, 3, foo="bar")
    e.success = True
    e.failure = False

    id = 1
    s = dump_event(e, id)
    x, id = load_event(s)

    assert hasattr(x, "args")
    assert hasattr(x, "kwargs")
    assert hasattr(x, "success")
    assert hasattr(x, "failure")
    assert hasattr(x, "channels")
    assert hasattr(x, "notify")


def test_values():
    from circuits.node.utils import dump_value, load_value
    from circuits.core.values import Value

    v = Value()
    v.value = 'foo'
    v.errors = False
    v.node_trn = 1

    s = dump_value(v)
    x, id, errors = load_value(s)

    assert v.value == x
    assert id == 1
    assert not errors
