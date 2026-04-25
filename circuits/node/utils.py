import json

from circuits.core import Event


META_EXCLUDE = set(dir(Event()))
META_EXCLUDE.add('node_call_id')
META_EXCLUDE.add('node_sock')
META_EXCLUDE.add('node_without_result')
META_EXCLUDE.add('success_channels')

META_ALLOWLIST = frozenset()


def load_event(s):
    data = json.loads(s)

    name = data['name']

    args = []
    for arg in data['args']:
        if isinstance(arg, str):
            arg = arg.encode('utf-8')
        args.append(arg)

    kwargs = {}
    for k, v in data['kwargs'].items():
        if isinstance(v, str):
            v = v.encode('utf-8')
        kwargs[str(k)] = v

    e = Event.create(name, *args, **kwargs)

    e.success = bool(data['success'])
    e.failure = bool(data['failure'])
    e.notify = bool(data['notify'])
    e.channels = tuple(data['channels'])

    meta = data.get('meta', {})
    if not isinstance(meta, dict):
        raise ValueError('Invalid event meta')

    for k, v in meta.items():
        if not isinstance(k, str):
            raise ValueError('Invalid event meta key')
        if k not in META_ALLOWLIST or k.startswith('_') or k in META_EXCLUDE:
            raise ValueError('Unsafe event meta key: %s' % k)
        if not isinstance(v, (type(None), bool, int, float, str, list, dict)):
            raise ValueError('Invalid event meta value: %s' % k)
        setattr(e, k, v)

    return e, data['id']


def dump_event(e, id):
    meta = {}
    for name in list((set(dir(e)) - META_EXCLUDE) & META_ALLOWLIST):
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
        for name in list((set(dir(e)) - META_EXCLUDE) & META_ALLOWLIST):
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
    return data['value'], data['id'], data['errors'], data['meta']
