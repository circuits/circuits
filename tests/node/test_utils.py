"""
test_utils

...
"""

import json

from circuits import Event
from circuits.core import Value
from circuits.node.utils import dump_event, dump_value, load_event, load_value


class test(Event):
    """test Event"""


def test_events():
    event = test(1, 2, 3, foo='bar')
    event.success = True
    event.failure = False
    event.test_meta = 1
    event._test_meta = 2
    event.__test_meta = 3

    id = 1
    faked = json.loads(dump_event(event, id))
    faked['meta']['__test_meta'] = 3
    event, id = load_event(json.dumps(faked))

    assert hasattr(event, 'args')
    assert hasattr(event, 'kwargs')
    assert hasattr(event, 'success')
    assert hasattr(event, 'failure')
    assert hasattr(event, 'channels')
    assert hasattr(event, 'notify')
    assert hasattr(event, 'test_meta')
    assert hasattr(event, '_test_meta')
    assert not hasattr(event, '__test_meta')


def test_values():
    event = Event()
    event.test_meta = 1
    event._test_meta = 2
    event.__test_meta = 3

    value = Value(event=event)
    value.value = 'foo'
    value.errors = False
    value.node_call_id = 1

    faked = json.loads(dump_value(value))
    faked['meta']['__test_meta'] = 3
    faked = json.dumps(faked)
    x, id, errors, meta = load_value(faked)

    assert value.value == x
    assert id == 1
    assert not errors
    assert meta['test_meta'] == event.test_meta
    assert meta['_test_meta'] == event._test_meta
    assert '__test_meta' not in meta
