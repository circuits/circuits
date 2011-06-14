# Package:  handlers
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Handlers

This module define the @handler decorator/function and the HandlesType type.
"""

from inspect import getargspec
from collections import Callable


def handler(*names, **kwargs):
    """Creates an Event Handler

    ...
    """

    def wrapper(f):
        if names and type(names[0]) is bool and not names[0]:
            f.handler = False
            return f

        f.handler = True

        f.names = names
        f.priority = kwargs.get("priority", 0)
        f.filter = kwargs.get("filter", False)
        f.channel = kwargs.get("channel", None)
        f.override = kwargs.get("override", False)
        f.tick = kwargs.get("tick", False)

        args = getargspec(f)[0]

        if args and args[0] == "self":
            del args[0]
        f.event = getattr(f, "event", bool(args and args[0] == "event"))

        return f

    return wrapper


def tick(f):
    return handler(f.__name__, tick=True)(f)


class HandlerMetaClass(type):

    def __init__(cls, name, bases, ns):
        super(HandlerMetaClass, cls).__init__(name, bases, ns)

        callables = (x for x in ns.items() if isinstance(x[1], Callable))
        for name, callable in callables:
            if not (name.startswith("_") or hasattr(callable, "handler")):
                setattr(cls, name, handler(name)(callable))
