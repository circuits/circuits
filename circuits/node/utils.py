import json

from circuits.core import Event
from circuits.six import PY3, text_type

META_EXCLUDE = set(dir(Event()))
META_EXCLUDE.add("node_call_id")
META_EXCLUDE.add("node_sock")
META_EXCLUDE.add("node_without_result")
META_EXCLUDE.add("success_channels")


def load_event(s):
    data = json.loads(s)

    name = data["name"] if PY3 else data["name"].encode("utf-8")

    args = []
    for arg in data["args"]:
        if isinstance(arg, text_type):
            arg = arg.encode("utf-8")
        args.append(arg)

    kwargs = {}
    for k, v in data["kwargs"].items():
        if isinstance(v, text_type):
            v = v.encode("utf-8")
        kwargs[str(k)] = v

    e = Event.create(name, *args, **kwargs)

    e.success = bool(data["success"])
    e.failure = bool(data["failure"])
    e.notify = bool(data["notify"])
    e.channels = tuple(data["channels"])

    for k, v in dict(data["meta"]).items():
        setattr(e, k, v)

    return e, data["id"]


def dump_event(e, id):
    meta = {}
    for name in list(set(dir(e)) - META_EXCLUDE):
        meta[name] = getattr(e, name)

    data = {
        "id": id,
        "name": e.name,
        "args": e.args,
        "kwargs": e.kwargs,
        "success": e.success,
        "failure": e.failure,
        "channels": e.channels,
        "notify": e.notify,
        "meta": meta
    }

    return json.dumps(data)


def dump_value(v):
    meta = {}
    e = v.event
    if e:
        for name in list(set(dir(e)) - META_EXCLUDE):
            meta[name] = getattr(e, name)

    data = {
        "id": v.node_call_id,
        "errors": v.errors,
        "value": v._value,
        "meta": meta
    }
    return json.dumps(data)


def load_value(v):
    data = json.loads(v)
    return data['value'], data['id'], data['errors'], data['meta']
