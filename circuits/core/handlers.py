"""
This module define the @handler decorator/function and the HandlesType type.
"""
try:
    from collections import Callable
except ImportError:
    from collections.abc import Callable

from circuits.tools import getargspec


def handler(*names, **kwargs):
    """Creates an Event Handler

    This decorator can be applied to methods of classes derived from
    :class:`circuits.core.components.BaseComponent`. It marks the method as a
    handler for the events passed as arguments to the ``@handler`` decorator.
    The events are specified by their name.

    The decorated method's arguments must match the arguments passed to the
    :class:`circuits.core.events.Event` on creation. Optionally, the
    method may have an additional first argument named *event*. If declared,
    the event object that caused the handler to be invoked is assigned to it.

    By default, the handler is invoked by the component's root
    :class:`~.manager.Manager` for events that are propagated on the channel
    determined by the BaseComponent's *channel* attribute.
    This may be overridden by specifying a different channel as a keyword
    parameter of the decorator (``channel=...``).

    Keyword argument ``priority`` influences the order in which handlers
    for a specific event are invoked. The higher the priority, the earlier
    the handler is executed.

    If you want to override a handler defined in a base class of your
    component, you must specify ``override=True``, else your method becomes
    an additional handler for the event.

    **Return value**

    Normally, the results returned by the handlers for an event are simply
    collected in the :class:`circuits.core.events.Event`'s :attr:`value`
    attribute. As a special case, a handler may return a
    :class:`types.GeneratorType`. This signals to the dispatcher that the
    handler isn't ready to deliver a result yet.
    Rather, it has interrupted it's execution with a ``yield None``
    statement, thus preserving its current execution state.

    The dispatcher saves the returned generator object as a task.
    All tasks are reexamined (i.e. their :meth:`next()` method is invoked)
    when the pending events have been executed.

    This feature avoids an unnecessarily complicated chaining of event
    handlers. Imagine a handler A that needs the results from firing an
    event E in order to complete. Then without this feature, the final
    action of A would be to fire event E, and another handler for
    an event ``SuccessE`` would be required to complete handler A's
    operation, now having the result from invoking E available
    (actually it's even a bit more complicated).

    Using this "suspend" feature, the handler simply fires event E and
    then yields ``None`` until e.g. it finds a result in E's :attr:`value`
    attribute. For the simplest scenario, there even is a utility
    method :meth:`circuits.core.manager.Manager.callEvent` that combines
    firing and waiting.
    """

    def wrapper(f):
        if names and isinstance(names[0], bool) and not names[0]:
            f.handler = False
            return f

        f.handler = True

        f.names = names
        f.priority = kwargs.get("priority", 0)
        f.channel = kwargs.get("channel", None)
        f.override = kwargs.get("override", False)

        args = getargspec(f)[0]

        if args and args[0] == "self":
            del args[0]
        f.event = getattr(f, "event", bool(args and args[0] == "event"))

        return f

    return wrapper


class Unknown(object):

    """Unknown Dummy Component"""


def reprhandler(handler):
    format = "<handler[%s][%s]%s (%s.%s)>"

    channel = getattr(handler, "channel", "*")
    if channel is None:
        channel = "*"

    from circuits.core.manager import Manager
    if isinstance(channel, Manager):
        channel = "<instance of " + channel.__class__.__name__ + ">"

    names = ",".join(handler.names)

    instance = getattr(
        handler, "im_self", getattr(
            handler, "__self__", Unknown()
        )
    ).__class__.__name__

    method = handler.__name__

    priority = "[%0.2f]" % (handler.priority,) if handler.priority else ""

    return format % (channel, names, priority, instance, method)


class HandlerMetaClass(type):

    def __init__(cls, name, bases, ns):
        super(HandlerMetaClass, cls).__init__(name, bases, ns)

        callables = (x for x in ns.items() if isinstance(x[1], Callable))
        for name, callable in callables:
            if not (name.startswith("_") or hasattr(callable, "handler")):
                try:
                    setattr(cls, name, handler(name)(callable))
                except ValueError as e:
                    raise ValueError('{} - {} {}'.format(str(e), repr(cls), name))
