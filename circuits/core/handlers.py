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
        f.channel = kwargs.get("channel", None)
        f.filter = kwargs.get("filter", False)
        f.priority = kwargs.get("priority", 0)
        f.override = kwargs.get("override", False)

        args = getargspec(f)[0]

        if args and args[0] == "self":
            del args[0]
        f.event = getattr(f, "event", bool(args and args[0] == "event"))

        return f

    return wrapper

class HandlerMetaClass(type):
    """Handler Meta Class

    metaclass used by the Component to pick up any methods defined in the
    new Component and turn them into Event Handlers by applying the
    @handlers decorator on them. This is done for all methods defined in
    the Component that:
    - Do not start with a single '_'. or
    - Have previously been decorated with the @handlers decorator
    """

    def __init__(cls, name, bases, dct):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(HandlerMetaClass, cls).__init__(name, bases, dct)

        for k, v in dct.items():
            if (isinstance(v, Callable)
                    and not (k[0] == "_" or hasattr(v, "handler"))):
                setattr(cls, k, handler(k)(v))
