# Package:  utils
# Date:     ...
# Author:   ...

"""Utils

...
"""


import json

from circuits.core import Event, Value


def load_event(s):
    data = json.loads(s)

    name = "".join(x.title() for x in str(data["name"]).split("_"))

    args = []
    for arg in data["args"]:
        if isinstance(arg, unicode):
            try:
                args.append(str(arg))
            except UnicodeDecodeError:
                args.append(arg)
        else:
            args.append(arg)

    kwargs = {}
    for k, v in data["kwargs"].items():
        if isinstance(v, unicode):
            try:
                kwargs[str(k)] = str(v)
            except UnicodeDecodeError:
                kwargs[str(k)] = v
        else:
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
