# Package:  utils
# Date:     ...
# Author:   ...

"""Utils

...
"""


import json

from circuits.core import Event
from circuits.six import bytes_to_str, text_type


def load_event(s):
    data = json.loads(s)

    name = bytes_to_str(data["name"].encode("utf-8"))

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

    return e, data["id"]


def dump_event(e, id):
    data = {
        "id": id,
        "name": e.name,
        "args": e.args,
        "kwargs": e.kwargs,
        "success": e.success,
        "failure": e.failure,
        "channels": e.channels,
        "notify": e.notify
    }

    return json.dumps(data)


def dump_value(v):
    data = {
        "id": v.node_trn,
        "errors": v.errors,
        "value": v._value,
    }
    return json.dumps(data)


def load_value(v):
    data = json.loads(v)
    return data['value'], data['id'], data['errors']
