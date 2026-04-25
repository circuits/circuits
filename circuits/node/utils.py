import json

from circuits.core import Event


META_EXCLUDE = set(dir(Event()))
META_EXCLUDE.add('node_call_id')
META_EXCLUDE.add('node_sock')
META_EXCLUDE.add('node_without_result')
META_EXCLUDE.add('success_channels')


def load_event(s):
    data = json.loads(s)

    name = data['name']
    args = data['args']
    kwargs = data['kwargs']
    e = Event.create(name, *args, **kwargs)

    e.success = bool(data['success'])
    e.failure = bool(data['failure'])
    e.notify = bool(data['notify'])
    e.channels = tuple(data['channels'])

    for k, v in dict(data['meta']).items():
        if k.startswith('__') or k in META_EXCLUDE:
            continue
        setattr(e, k, v)

    return e, data['id']


def dump_event(e, id):
    meta = {}
    for name in list(set(dir(e)) - META_EXCLUDE):
        meta[name] = getattr(e, name)

    data = {
        'id': id,
        'name': e.name,
        'args': e.args,
        'kwargs': e.kwargs,
        'success': e.success,
        'failure': e.failure,
        'channels': e.channels,
        'notify': e.notify,
        'meta': meta,
    }

    return json.dumps(data)


def dump_value(v):
    meta = {}
    e = v.event
    if e:
        for name in list(set(dir(e)) - META_EXCLUDE):
            if not name.startswith('__'):
                meta[name] = getattr(e, name)

    data = {
        'id': v.node_call_id,
        'errors': v.errors,
        'value': v._value,
        'meta': meta,
    }
    return json.dumps(data)


def load_value(v):
    data = json.loads(v)
    meta = {k: v for k, v in data['meta'].items() if not k.startswith('__') and k not in META_EXCLUDE}
    return data['value'], data['id'], data['errors'], meta
