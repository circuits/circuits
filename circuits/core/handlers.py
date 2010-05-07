# Package:  handlers
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Handlers

This module define the @handler decorator/function and the HandlesType type.
"""

from inspect import getargspec

def handler(*channels, **kwargs):
    """Creates an Event Handler

    Decorator to wrap a callable into an Event Handler that
    listens on a set of channels defined by channels. The type
    of the Event Handler defaults to "listener". If kwargs["filter"]
    is defined and is True, the Event Handler is defined as a
    Filter and has priority over Listener Event Handlers.
    If kwargs["target"] is defined and is not None, the
    Event Handler will listen for the spcified channels on the
    spcified Target Component's Channel.
    
    Examples:
       >>> @handler("foo")
       ... def foo():
       ...     pass
       >>> @handler("bar", filter=True)
       ... def bar():
       ...     pass
       >>> @handler("foo", "bar")
       ... def foobar():
       ...     pass
       >>> @handler("x", target="other")
       ... def x():
       ...     pass
    """

    def wrapper(f):
        if channels and type(channels[0]) is bool and not channels[0]:
            f.handler = False
            return f

        f.handler = True

        f.channels = channels
        f.target = kwargs.get("target", None)
        f.filter = kwargs.get("filter", False)
        f.priority = kwargs.get("priority", 0)
        f.override = kwargs.get("override", False)

        args = getargspec(f)[0]

        if args and args[0] == "self":
            del args[0]
        f.event = bool(args and args[0] == "event")

        return f

    return wrapper

class HandlersType(type):
    """Handlers metaclass

    metaclass used by the Component to pick up any methods defined in the
    new Component and turn them into Event Handlers by applying the
    @handlers decorator on them. This is done for all methods defined in
    the Component that:
     - Do not start with a single '_'. or
     - Have previously been decorated with the @handlers decorator
    """

    def __init__(cls, name, bases, dct):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(HandlersType, cls).__init__(name, bases, dct)

        for k, v in dct.iteritems():
            if callable(v) and not (k[0] == "_" or hasattr(v, "handler")):
                setattr(cls, k, handler(k)(v))
