# Module:   core
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Building Blocks

This module contains the most basic building blocks of all Components.
It's important to note that a Component is also a Manager.

The following import statement is commonly used:
   >>> from circuits import handler, Event, Component, Manager
"""

import new
import time
import warnings
from itertools import chain
from threading import Thread
from functools import partial
from collections import deque
from operator import attrgetter
from collections import defaultdict
from sys import exc_info as _exc_info
from sys import exc_clear as _exc_clear
from inspect import getargspec, getmembers
from signal import signal, SIGHUP, SIGINT, SIGTERM

try:
    from threading import current_thread as thread
except ImportError:
    from threading import currentThread as thread

try:
    from multiprocessing import Process
    from multiprocessing import current_process as process
    from multiprocessing import active_children as processes
    HAS_MULTIPROCESSING = 2
except ImportError:
    try:
        from processing import Process
        from processing import currentProcess as process
        from processing import activeChildren as processes
        HAS_MULTIPROCESSING = 1
    except ImportError:
        HAS_MULTIPROCESSING = 0


class Event(object):
    """Create a new Event Object

    Create a new Event Object populating it with the given list of arguments
    and keyword arguments.

    @ivar name:    The name of the Event
    @ivar channel: The channel this Event is bound for
    @ivar target:  The target Component's channel this Event is bound for

    @param args: list of arguments
    @type  args: tuple

    @param kwargs: dct of keyword arguments
    @type  kwargs: dict
    """

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        self.args = args
        self.kwargs = kwargs

        self.name = self.__class__.__name__
        self.channel = None
        self.target = None

    def __eq__(self, y):
        """ x.__eq__(y) <==> x==y

        Tests the equality of Event self against Event y.
        Two Events are considered "equal" iif the name,
        channel and target are identical as well as their
        args and kwargs passed.
        """

        attrs = ("name", "args", "kwargs", "channel", "target")
        return all([getattr(self, a) == getattr(y, a) for a in attrs])

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

        Get and return data from the Event object requested by "x".
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
    """Error Event

    This Event is sent for any exceptions that occur during the execution
    of an Event Handler that is not SystemExit or KeyboardInterrupt.

    @param type: type of exception
    @type type: type

    @param value: exception object
    @type value: exceptions.TypeError

    @param traceback: traceback of exception
    @type traceback: traceback
    """

    def __init__(self, type, value, traceback):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(type, value, traceback)


class Started(Event):
    """Started Event

    This Event is sent when a Component has started running.

    @param component: The component that was started
    @type  component: Component or Manager

    @param mode: The mode in which the Component was started,
                 P (Process), T (Thread) or None (Main Thread / Main Process).
    @type  str:  str or None
    """

    def __init__(self, component, mode):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Started, self).__init__(component, mode)


class Stopped(Event):
    """Stopped Event

    This Event is sent when a Component has stopped running.

    @param component: The component that has stopped
    @type  component: Component or Manager
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Stopped, self).__init__(component)

class Signal(Event):
    """Signal Event

    This Event is sent when a Component receives a signal.

    @param signal: The signal number received.
    @type  int:    An int value for the signal

    @param stack:  The interrupted stack frame.
    @type  object: A stack frame
    """

    def __init__(self, signal, stack):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Signal, self).__init__(signal, stack)


class Registered(Event):
    """Registered Event

    This Event is sent when a Component has registered with another Component
    or Manager. This Event is only sent iif the Component or Manager being
    registered with is not itself.

    @param component: The Component being registered
    @type  component: Component

    @param manager: The Component or Manager being registered with
    @type  manager: Component or Manager
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Registered, self).__init__(component, manager)

class Unregistered(Event):
    """Unregistered Event

    This Event is sent when a Component has been unregistered from it's
    Component or Manager.
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregistered, self).__init__(component, manager)


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

    @deprecated: The use of 'type' in kwargs will be deprecated in 1.2
                 Use 'filter' instead.
    """

    def wrapper(f):
        f.handler = True

        f.override = kwargs.get("override", False)
        f.priority = kwargs.get("priority", 0)

        if "type" in kwargs:
            warnings.warn("Please use 'filter', 'type' will be deprecated in 1.2")
            f.filter = kwargs.get("type", "listener") == "filter"
        else:
            f.filter = kwargs.get("filter", False)

        f.target = kwargs.get("target", None)
        f.channels = channels

        _argspec = getargspec(f)
        _args = _argspec[0]
        if _args and _args[0] == "self":
            del _args[0]
        if _args and _args[0] == "event":
            f._passEvent = True
        else:
            f._passEvent = False

        return f

    return wrapper

def listener(*channels, **kwargs):
    "@deprecated: This is planned to be deprecated in 1.2 Use handlers instead"

    warnings.warn("Please use @handler, @listener will be deprecated in 1.2")
    return handler(*channels, **kwargs)

class HandlersType(type):
    """Handlers metaclass

    metaclass used by the Component to pick up any methods defined in the new
    Component and turn them into Event Handlers by applying the @handlers
    decorator on them. This is done for all methods defined in the Component
    that:
     - Do not start with a single '_'. or
     - Have previously been decorated with the @handlers decorator
    """

    def __init__(cls, name, bases, dct):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(HandlersType, cls).__init__(name, bases, dct)

        for k, v in dct.iteritems():
            if callable(v) and not (k[0] == "_" or hasattr(v, "handler")):
                setattr(cls, k, handler(k)(v))


class Manager(object):
    """Manager

    This is the base Manager of the BaseComponent which manages an Event Queue,
    a set of Event Handlers, Channels, Tick Functions, Registered and Hidden
    Components, a Task and the Running State.

    @ivar manager: The Manager of this Component or Manager
    """

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self._queue = deque()
        self._handlers = set()
        self._channels = defaultdict(list)

        self._ticks = set()
        self._components = set()

        self._task = None
        self._running = False

        self.manager = self

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__
        q = len(self._queue)
        c = len(self._channels)
        h = len(self._handlers)
        state = self.state
        format = "<%s (q: %d c: %d h: %d) [%s]>"
        return format % (name, q, c, h, state)

    def __len__(self):
        """x.__len__() <==> len(x)

        Returns the number of events in the Event Queue.
        """

        return len(self._queue)

    def __add__(self, y):
        """x.__add__(y) <==> x+y

        (Optional) Convenience operator to register y with x
        Equivalent to: y.register(x)

        @return: x
        @rtype Component or Manager
        """

        y.register(self)
        return self
    
    def __iadd__(self, y):
        """x.__iadd__(y) <==> x += y

        (Optional) Convenience operator to register y with x
        Equivalent to: y.register(x)

        @return: x
        @rtype Component or Manager
        """

        y.register(self)
        return self

    def __sub__(self, y):
        """x.__sub__(y) <==> x-y

        (Optional) Convenience operator to unregister y from x.manager
        Equivalent to: y.unregister()

        @return: x
        @rtype Component or Manager
        """

        if y.manager == self:
            y.unregister()
            return self
        else:
            raise TypeError("No registration found for %r" % y)

    def __isub__(self, y):
        """x.__sub__(y) <==> x -= y

        (Optional) Convenience operator to unregister y from x
        Equivalent to: y.unregister()

        @return: x
        @rtype Component or Manager
        """

        if y.manager == self:
            y.unregister()
            return self
        else:
            raise TypeError("No registration found for %r" % y)

    def _getHandlers(self, s):
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

    @property
    def state(self):
        if self._running:
            if self._task is None:
                return "R"
            else:
                if self._task.is_alive():
                    return "R"
                else:
                    return "D"
        else:
            return "S"

    @property
    def running(self):
        return self._running

    @property
    def components(self):
        return self._components

    @property
    def channels(self):
        return self._channels

    @property
    def ticks(self):
        return self._ticks

    def _add(self, handler, channel=None):
        """E._add(handler, channel) -> None

        Add a new Event Handler to the Event Manager
        adding it to the given channel. If no channel is
        given, add it to the global channel.
        """

        self._handlers.add(handler)

        if channel is None:
            channel = "*"

        if channel in self.channels:
            if handler not in self.channels[channel]:
                self._channels[channel].append(handler)
                self._channels[channel].sort(
                        key=attrgetter("priority", "filter"))
                self._channels[channel].reverse()
        else:
            self._channels[channel] = [handler]

    def _remove(self, handler, channel=None):
        """E._remove(handler, channel=None) -> None

        Remove the given Event Handler from the Event Manager
        removing it from the given channel. if channel is None,
        remove it from all channels. This will succeed even
        if the specified  handler has already been removed.
        """

        if channel is None:
            channels = self.channels.keys()
        else:
            channels = [channel]

        if handler in self._handlers:
            self._handlers.remove(handler)

        for channel in channels:
            if handler in self.channels[channel]:
                self._channels[channel].remove(handler)
            if not self._channels[channel]:
                del self._channels[channel]


    def push(self, event, channel, target=None):
        """Push a new Event into the queue

        This will push the given Event, Channel and Target onto the
        Event Queue for later processing.

        if target is None, then target will be set as the Channel of
        the current Component, self.channel (defaulting back to None).

        If this Component's Manager is itself, enqueue on this Component's
        Event Queue, otherwise enqueue on this Component's Manager.

        @param event: The Event Object
        @type  event: Event

        @param channel: The Channel this Event is bound for
        @type  channel: str

        @keyword target: The target Component's channel this Event is bound for
        @type    target: str or Component
        """

        if target is None:
            target = getattr(self, "channel", None)

        if self.manager == self:
            self._queue.append((event, channel, target))
        else:
            self.manager.push(event, channel, target)

    def flush(self):
        """Flush all Events in the Event Queue

        This will flush all Events in the Event Queue. If this Component's
        Manager is itself, flush all Events from this Component's Event Queue,
        otherwise, flush all Events from this Component's Manager's Event Queue.
        """

        if self.manager == self:
            q = self._queue
            self._queue = deque()
            while q:
                event, channel, target = q.popleft()
                self.send(event, channel, target)
        else:
            self.manager.flush()

    def send(self, event, channel, target=None, errors=False, log=True):
        """Send a new Event to Event Handlers for the Target and Channel

        This will send the given Event, to the spcified CHannel on the
        Target Component's Channel.

        if target is None, then target will be set as the Channel of
        the current Component, self.channel (defaulting back to None).

        If this Component's Manager is itself, enqueue on this Component's
        Event Queue, otherwise enqueue on this Component's Manager.

        @param event: The Event Object
        @type  event: Event

        @param channel: The Channel this Event is bound for
        @type  channel: str

        @keyword target: The target Component's channel this Event is bound for
        @type    target: str or Component

        @keyword errors: True to raise errors, False otherwise
        @type    errors: bool

        @keyword log: True to log errors, False otherwise
        @type    log: bool

        @return: The return value of the last executed Event Handler
        @rtype:  object
        """

        if target is None:
            target = getattr(self, "channel", None)

        if self.manager == self:
            event.channel = channel
            event.target = target
            eargs = event.args
            ekwargs = event.kwargs
            if target is not None and isinstance(target, Component):
                target = getattr(target, "channel", None)
            if target is not None and type(target) == str:
                channel = "%s:%s" % (target, channel)

            r = False
            for handler in self._getHandlers(channel):
                try:
                    if handler._passEvent:
                        r = partial(handler, event, *eargs, **ekwargs)()
                    else:
                        r = partial(handler, *eargs, **ekwargs)()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    if log:
                        self.push(Error(*_exc_info()), "error")
                    if errors:
                        raise
                    else:
                        _exc_clear()
                if r is not None and r and handler.filter:
                    return r
            return r
        else:
            return self.manager.send(event, channel, target, errors, log)

    def _signal(self, signal, stack):
        if not self.send(Signal(signal, stack), "signal"):
            if signal == SIGINT:
                raise KeyboardInterrupt
            elif signal == SIGTERM:
                raise SystemExit

    def start(self, sleep=0, errors=True, log=True, process=False):
        group = None
        target = self.run
        name = self.__class__.__name__
        mode = "P" if process else "T"
        args = (sleep, mode, errors, log,)

        if process and HAS_MULTIPROCESSING:
            args += (self,)
            self._task = Process(group, target, name, args)
            if HAS_MULTIPROCESSING == 1:
                setattr(self._task, "is_alive", self._task.isAlive)
            self._task.start()
            return

        self._task = Thread(group, target, name, args)
        self._task.setDaemon(True)
        self._task.start()

    def stop(self):
        self._running = False
        if hasattr(self._task, "terminate"):
            self._task.terminate()
        if hasattr(self._task, "join"):
            self._task.join(3)
        self._task = None

    def _terminate(self):
        if HAS_MULTIPROCESSING:
            for p in processes():
                if not p == process():
                    p.terminate()
                    p.join(3)

    def run(self, sleep=0, mode=None, errors=False, log=True, __self=None):
        if __self is not None:
            self = __self

        if not mode == "T":
            signal(SIGHUP, self._signal)
            signal(SIGINT, self._signal)
            signal(SIGTERM, self._signal)

        self._running = True

        self.push(Started(self, mode), "started")

        try:
            while self._running:
                try:
                    [f() for f in self.ticks.copy()]
                    self.flush()
                    if sleep:
                        try:
                            time.sleep(sleep)
                        except:
                            pass
                except (KeyboardInterrupt, SystemExit):
                    self._running = False
                except:
                    try:
                        if log:
                            self.push(Error(*_exc_info()), "error")
                        if errors:
                            raise
                        else:
                            _exc_clear()
                    except:
                        pass
        finally:
            try:
                self.push(Stopped(self), "stopped")
                rtime = time.time()
                while len(self) > 0 and (time.time() - rtime) < 3:
                    [f() for f in self.ticks.copy()]
                    self.flush()
                    if sleep:
                        time.sleep(sleep)
                    rtime = time.time()
            except:
                pass

class BaseComponent(Manager):
    """Base Component

    This is the Base of the Component which manages registrations to other
    components or managers. Every Base Component and thus Component has a
    unique Channel that is used as a separation of concern for it's registered
    Event Handlers. By default, this Channels is None (or also known as the
    Global Channel).

    When a Component (Base Component) has a set Channel that is not the Global
    Channel (None), then any Event Handlers will actually listen on a Channel
    that is a combination of the Component's Channel prefixed with the Event
    Handler's Channel. The form becomes:

    C{target:channel}

    Where:
       - target is the Component's Channel
       - channel is the Event Handler's Channel

    @ivar channel: The Component's Channel
    """

    channel = None

    def __new__(cls, *args, **kwargs):
        """TODO Work around for Python bug.

        Bug: http://bugs.python.org/issue5322
        """

        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(BaseComponent, self).__init__(*args, **kwargs)

        self.channel = kwargs.get("channel", self.channel)
        self.register(self)

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__
        channel = self.channel or ""
        q = len(self._queue)
        c = len(self._channels)
        h = len(self._handlers)
        state = self.state
        format = "<%s/%s (q: %d c: %d h: %d) [%s]>"
        return format % (name, channel, q, c, h, state)

    def __call__(self, channel, *args, **kwargs):
        """x.__call__(...) <==> x(...)

        (Optional) Convenience callable to send an arbitary Event to
        the given Channel populating the Event OBject with the given
        *args and **kwargs and returning the result.

        @return: Result of sending Event to Channel with (*args, **kwargs)
        @rtype object
        """


        e = Event(*args, **kwargs)
        e.name = channel.title()
        return self.send(e, channel, self.channel)

    def _registerHandlers(self, manager):
        p = lambda x: callable(x) and getattr(x, "handler", False)
        handlers = [v for k, v in getmembers(self, p)]

        for handler in handlers:
            if handler.channels:
                channels = handler.channels
            else:
                channels = ["*"]

            for channel in channels:
                if handler.target is not None:
                    target = handler.target
                else:
                    target = self.channel

                if target is not None:
                    channel = "%s:%s" % (target, channel)

                manager._add(handler, channel)

    def _unregisterHandlers(self, manager):
        for handler in self._handlers.copy():
            manager._remove(handler)

    def register(self, manager):
        """Register all Event Handlers with the given Manager
        
        This will register all Event Handlers of this Component to the
        given Manager. By default, every Component (Base Component) is
        registered with itself.
        
        Iif the Component or Manager being registered
        with is not the current Component, then any Hidden Components
        in registered to this Component will also be regsitered with the
        given Manager. A Registered Event will also be sent.
        """

        def _root(x):
            if x.manager == x:
                return x
            else:
                return _root(x.manager)

        def _register(c, m, r):
            c._registerHandlers(m)
            if m is not r:
                c._registerHandlers(r)
            if hasattr(c, "__tick__"):
                m._ticks.add(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.add(getattr(c, "__tick__"))
            for x in c.components:
                _register(x, m, r)

        _register(self, manager, _root(manager))

        self.manager = manager

        if manager is not self:
            manager._components.add(self)
            self.push(Registered(self, manager), "registered", self.channel)

    def unregister(self):
        """Unregister all registered Event Handlers
        
        This will unregister all registered Event Handlers of this Component
        from it's registered Component or Manager.

        @note: It's possible to unregister a Component from itself!
        """

        def _root(x):
            if x.manager == x:
                return x
            else:
                return _root(x.manager)

        def _unregister(c, m, r):
            c._unregisterHandlers(m)
            if m is not r:
                c._unregisterHandlers(r)
            if hasattr(c, "__tick__"):
                m._ticks.remove(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.remove(getattr(c, "__tick__"))

            for x in c.components:
                _unregister(x, m, r)

        _unregister(self, self.manager, _root(self.manager))

        if self in self.manager._components:
            self.manager._components.remove(self)

        self.push(Unregistered(self, self.manager), "unregistered", self.channel)

        self.manager = self

class Component(BaseComponent):
    "Component"

    __metaclass__ = HandlersType

    def __new__(cls, *args, **kwargs):
        self = BaseComponent.__new__(cls, *args, **kwargs)
        handlers = [x for x in cls.__dict__.values() \
                if getattr(x, "handler", False)]
        overridden = lambda x: [h for h in handlers \
                if x.channels == h.channels and getattr(h, "override", False)]
        for base in cls.__bases__:
            if issubclass(cls, base):
                for k, v in base.__dict__.iteritems():
                    p1 = callable(v)
                    p2 = getattr(v, "handler", False)
                    predicate = p1 and p2 and not overridden(v)
                    if predicate:
                        name = "%s_%s" % (base.__name__, k)
                        method = new.instancemethod(v, self, cls)
                        setattr(self, name, method)
        return self
