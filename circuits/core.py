# Module:   core
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
Core of the circuits library containing all of the essentials for a
circuits based application or system. Normal usage of circuits:

>>> from circuits import listener, Manager, Component, Event
"""

from itertools import chain
from collections import deque
from collections import defaultdict
from inspect import getargspec, getmembers


class InvalidHandler(Exception):
    """Invalid Handler Exception

    Invalid Handler Exception raised when adding a callable
    to a manager that was not decorated with the
    :func:`listener decorator <circuits.core.listener>`.
    """

    def __init__(self, handler):
        "initializes x; see x.__class__.__doc__ for signature"

        super(InvalidHandler, self).__init__()

        self.handler = handler


class Event(object):
    """Create a new Event Object

    Create a new event object populating it with the given
    list of arguments and keyword arguments.

    :param args: list of arguments for this event
    :type args: list/tuple or iterable
    :param kwargs: keyword arguments for this event
    :type kwargs: dict
    """

    channel = None
    target = None

    source = None  # Used by Bridge
    ignore = False # Used by Bridge

    def __new__(cls, *args, **kwargs):
        self = object.__new__(Event)
        self.name = cls.__name__
        self.args = args
        self.kwargs = kwargs
        return self

    def __eq__(self, y):
        """ x.__eq__(y) <==> x==y

        Tests the equality of event self against event y.
        Two events are considered "equal" iif the name,
        channel and target are identical as well as their
        args and kwargs passed.
        """

        attrs = ["name", "args", "kwargs", "channel", "target"]
        r = [getattr(self, a) == getattr(y, a) for a in attrs]
        return False not in r

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        if self.channel is not None and self.target is not None:
            channelStr = "%s:%s" % (self.target, self.channel)
        elif self.channel is not None:
            channelStr = self.channel
        else:
            channelStr = ""
        argsStr = ", ".join([("%s" % repr(arg)) for arg in self.args])
        kwargsStr = ", ".join(
                [("%s=%s" % kwarg) for kwarg in self.kwargs.iteritems()])
        return "<%s[%s] (%s, %s)>" % (self.name, channelStr, argsStr, kwargsStr)

    def __getitem__(self, x):
        """x.__getitem__(y) <==> x[y]

        Get and return data from the event object requested by "x".
        If an int is passed to x, the requested argument from self.args
        is returned index by x. If a str is passed to x, the requested
        keyword argument from self.kwargs is returned keyed by x.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if type(x) == int:
            return self.args[x]
        elif type(x) == str:
            return self.kwargs[x]
        else:
            raise TypeError("Expected int or str, got %r" % type(x))


class Error(Event):
    """Error(error) -> Error Event

    error: An exception object
    """

def listener(*args, **kwargs):
    """Creates an Event Handler of a callable object

    Decorator to wrap a callable into an event handler that
    listens on a set of channels defined by args. The type
    of the listener defaults to "listener" and is defined
    by kwargs["type"]. To define a filter, pass type="filter"
    to kwargs. If kwargs["target"] is not None, this event handler
    will be registered and will ignore the channel of it's containing
    Component.
    
    Examples:

    >>> from circuits.core import listener
    >>> @listener("foo")
    ... def onFOO():
    ...     pass
    >>> @listener("bar", type="filter")
    ... def onBAR():
    ...     pass
    >>> @listener("foo", "bar")
    ... def onFOOBAR():
    ...     pass
    """

    def decorate(f):
        f.type = kwargs.get("type", "listener")
        f.target = kwargs.get("target", None)
        f.channels = args

        argspec = getargspec(f)
        _args = argspec[0]
        varargs = (True if argspec[1] else False)
        varkw = (True if argspec[2] else False)
        if _args and _args[0] == "self":
            del _args[0]

        if _args and _args[0] == "event":
            f.br = 1
        elif _args:
            f.br = 2
        else:
            if varargs and varkw:
                f.br = 2
            elif varkw:
                f.br = 3
            elif varargs:
                f.br = 4
            else:
                f.br = 5

        return f
    return decorate


class HandlersType(type):

    def __init__(cls, name, bases, dct):
        super(HandlersType, cls).__init__(name, bases, dct)

        for name, f in dct.iteritems():
            if callable(f) and not (name[0] == "_" or hasattr(f, "type")):
                setattr(cls, name, listener(name, type="listener")(f))


class Manager(object):
    """Creates a new Manager

    Create a new event manager which manages Components and Events.
    """

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Manager, self).__init__()

        self._queue = deque()

        self._handlers = set()

        self.manager = self
        self.channels = defaultdict(list)

    def __repr__(self):
        q = len(self._queue)
        h = len(self._handlers)
        return "<Manager (q: %d h: %d)>" % (q, h)

    def __getitem__(self, x):
        return self.channels[x]

    def __len__(self):
        return len(self._queue)

    def __add__(self, y):
        y.register(self.manager)
        if hasattr(y, "registered"):
            y.registered()
        return self
    
    def __iadd__(self, y):
        y.register(self.manager)
        if hasattr(y, "registered"):
            y.registered()
        return self

    def __sub__(self, y):
        if y.manager == self:
            y.unregister()
            if hasattr(y, "unregistered"):
                y.unregistered()
            return self
        else:
            raise TypeError("No registration found for %r" % y)

    def __isub__(self, y):
        if y.manager == self:
            y.unregister()
            if hasattr(y, "unregistered"):
                y.unregistered()
            return self
        else:
            raise TypeError("No registration found for %r" % y)

    def handlers(self, s):
        if s == "*:*":
            return self._handlers

        if ":" in s:
            target, channel = s.split(":", 1)
        else:
            channel = s
            target = None

        channels = self.channels
        globals = channels["*"]

        if target == "*":
            c = ":%s" % channel
            x = [channels[k] for k in channels if k == channel or k.endswith(c)]
            all = [i for y in x for i in y]
            return chain(globals, all)

        if channel == "*":
            c = "%s:" % target
            x = [channels[k] for k in channels if k.startswith(c) or ":" not in k]
            all = [i for y in x for i in y]
            return chain(globals, all)

        handlers = globals
        if channel in channels:
            handlers = chain(handlers, channels[channel])
        if target and "%s:*" % target in channels:
            handlers = chain(handlers, channels["%s:*" % target])
        if "*:%s" % channel in channels:
            handlers = chain(handlers, channels["*:%s" % channel])
        if target:
            handlers = chain(handlers, channels[s])

        return handlers


    def add(self, handler, channel=None):
        """E.add(handler, channel) -> None

        Add a new filter or listener to the event manager
        adding it to the given channel. If no channel is
        given, add it to the global channel.
        """

        if getattr(handler, "type", None) not in ["filter", "listener"]:
            raise InvalidHandler(handler)

        self._handlers.add(handler)

        if channel is None:
            channel = "*"

        if channel in self.channels:
            if handler not in self.channels[channel]:
                self.channels[channel].append(handler)
                self.channels[channel].sort(key=lambda x: x.type)
        else:
            self.channels[channel] = [handler]

    def remove(self, handler, channel=None):
        """E.remove(handler, channel=None) -> None

        Remove the given filter or listener from the
        event manager removing it from the given channel.
        if channel is None, remove it from the global
        channel. This will succeed even if the specified
        handler has already been removed.
        """

        if channel is None:
            if handler in self.channels["*"]:
                self.channels["*"].remove(handler)
            keys = self.channels.keys()
        else:
            keys = [channel]

        if handler in self._handlers:
            self._handlers.remove(handler)

        for channel in keys:
            if handler in self.channels[channel]:
                self.channels[channel].remove(handler)


    def push(self, event, channel, target=None):
        """E.push(event, channel, target=None) -> None

        Push the given event onto the given channel.
        This will queue the event up to be processed later
        by flushEvents. If target is given, the event will
        be queued for processing by the component given by
        target.
        """

        if self.manager == self:
            self._queue.append((event, channel, target))
        else:
            self.manager.push(event, channel, target)

    def flush(self):
        """E.flushEvents() -> None

        Flush all events waiting in the queue.
        Any event waiting in the queue will be sent out
        to filters/listeners.
        """

        if self.manager == self:
            q = self._queue
            self._queue = deque()
            while q:
                event, channel, target = q.pop()
                self.send(event, channel, target)
        else:
            self.manager.flush()

    def send(self, event, channel, target=None):
        """E.send(event, channel, target=None) -> None

        Send the given event to filters/listeners on the
        channel specified. If target is given, send this
        event to filters/listeners of the given target
        component.
        """

        if self.manager == self:
            event.channel = channel
            event.target = target
            eargs = event.args
            ekwargs = event.kwargs
            if target is not None:
                channel = "%s:%s" % (target, channel)

            r = False
            for handler in self.handlers(channel):
                br = handler.br

                if br == 1:
                    r = handler(event, *eargs, **ekwargs)
                elif br == 2:
                    r = handler(*eargs, **ekwargs)
                elif br == 3:
                    r = handler(**ekwargs)
                elif br == 4:
                    r = handler(*eargs)
                else:
                    r = handler()

                if r is not None and r and handler.type == "filter":
                    break
            return r
        else:
            return self.manager.send(event, channel, target)


    def iter(self, event, channel, target=None):
        """E.iter(event, channel, target=None) -> Generator

        Iterate and Send the given event to filters/listeners
        on the channel specified. If target is given, send this
        event to filters/listeners of the given target component.
        For each event that is sent, yield it's return result.
        """

        if self.manager == self:
            event.channel = channel
            event.target = target
            eargs = event.args
            ekwargs = event.kwargs
            if target is not None:
                channel = "%s:%s" % (target, channel)

            r = False
            for handler in self.handlers(channel):
                br = handler.br

                if br == 1:
                    r = handler(event, *eargs, **ekwargs)
                elif br == 2:
                    r = handler(*eargs, **ekwargs)
                elif br == 3:
                    r = handler(**ekwargs)
                elif br == 4:
                    r = handler(*eargs)
                else:
                    r = handler()

                yield r

                if r is not None and r and handler.type == "filter":
                    break
        else:
            for i in self.manager.iter(event, channel, target):
                yield i


class BaseComponent(Manager):
    """Creates a new Component

    Subclasses of Component define Event Handlers by decorating
    methods by using the listener decorator.

    All listeners found in the Component will automatically be
    picked up when the Component is instantiated.

    :param channel: channel this Component listens on (*default*: ``None``)
    :type channel: str
    """

    channel = None

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(BaseComponent, self).__init__(*args, **kwargs)

        self.channel = kwargs.get("channel", self.channel)
        self.register(self)


    def __repr__(self):
        name = self.__class__.__name__
        channel = self.channel or ""
        q = len(self._queue)
        h = len(self._handlers)
        return "<%s/%s component (q: %d h: %d)>" % (name, channel, q, h)

    def register(self, manager):
        handlers = [x[1] for x in getmembers(self) if callable(x[1]) and
                hasattr(x[1], "type")]

        for handler in handlers:
            if handler.channels:
                channels = handler.channels
            else:
                channels = ["*"]

            for channel in channels:
                if self.channel is not None:
                    if handler.target is not None:
                        target = handler.target
                    else:
                        target = self.channel

                    channel = "%s:%s" % (target, channel)

                manager.add(handler, channel)

        self.manager = manager


    def unregister(self):
        "Unregister all registered event handlers from the manager."

        for handler in self._handlers.copy():
            self.manager.remove(handler)

        self.manager = self

class Component(BaseComponent):

    __metaclass__ = HandlersType
