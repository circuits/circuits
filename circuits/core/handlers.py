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

    This decorator can be applied to methods of classes derived from
    :class:`circuits.core.components.BaseComponent`. It marks the 
    method as a handler for the events passed as arguments
    to the ``@handler`` decorator. The events are specified by their name.
    
    The decorated method's arguments must match the arguments passed to the
    :class:`circuits.core.events.Event` on creation. Optionally, the
    method may have an additional first argument named *event*. If declared,
    the event object that caused the handler to be invoked is assigned to it.
    
    By default, the handler is invoked for events that are propagated on
    the channel determined by the BaseComponent's *channel* attribute.
    This may be overridden by specifying a different channel as a keyword
    parameter of the decorator (``channel=...``).
    
    Keyword argument ``priority`` influences the order in which handlers
    for a specific event are invoked. The higher the priority, the earlier
    the handler is executed.
    
    A handler may also be specified as a filter by adding
    the keyword argument ``filter=True`` to the decorator.
    If such a handler returns a value different from ``None``, no more
    handlers are invoked for the handled event. Filtering handlers are
    invoked before normal handlers with the same priority (but after any
    handlers with higher priority).
    
    If you want to override a handler defined in a base class of your
    component, you must specify ``override=True``, else your method becomes
    an additional handler for the event.
    
    Finally, a handler may be defined as a "tick"-handler by
    specifying ``tick=True``.
    Such a handler is invoked at regular intervals ("polling").
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
