# Package:  handlers
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Handlers

This module define the @handler decorator/function and the HandlesType type.
"""

from copy import copy
from types import MethodType
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
        im_self = None
        if type(f) is MethodType:
            im_func = f.im_func
            im_self = f.im_self
            func_name = im_func.func_name
            f = copy(im_func)

        if channels and type(channels[0]) is bool and not channels[0]:
            f.handler = False
            return f

        f.handler = True

        f.override = kwargs.get("override", False)
        f.priority = kwargs.get("priority", 0)

        f.filter = kwargs.get("filter", False)

        f.target = kwargs.get("target", None)
        f.channels = channels

        f.args, f.varargs, f.varkw, f.defaults = getargspec(f)

        if f.args and f.args[0] == "self":
            del f.args[0]
        if f.args and f.args[0] == "event":
            f._passEvent = True
        else:
            f._passEvent = False

        if im_self is not None:
            f = MethodType(f, im_self)
            setattr(im_self, func_name, f)

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
