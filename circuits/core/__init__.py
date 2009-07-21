# Package:  core
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core Building Blocks

This package contains the most basic building blocks of all Components.
"""

import os
import new
import time
from itertools import chain
from threading import Thread
from collections import deque
from operator import attrgetter
from sys import exc_info as _exc_info
from sys import exc_clear as _exc_clear
from inspect import getargspec, getmembers

if os.name == "posix":
    from signal import signal, SIGHUP, SIGINT, SIGTERM
elif os.name in ["nt", "java"]:
    from signal import signal, SIGINT, SIGTERM
else:
    raise RuntimeError("Unsupported platform '%s'" % os.name)

try:
    from multiprocessing import Process
    from multiprocessing import current_process as process
    from multiprocessing import active_children as processes
    HAS_MULTIPROCESSING = 2
except:
    try:
        from processing import Process
        from processing import currentProcess as process
        from processing import activeChildren as processes
        HAS_MULTIPROCESSING = 1
    except:
        HAS_MULTIPROCESSING = 0

from circuits.tools import reprhandler, findroot

class Event(object):
    """Create a new Event Object

    Create a new Event Object populating it with the given list of arguments
    and keyword arguments.

    @ivar name:    The name of the Event
    @ivar channel: The channel this Event is bound for

    @param args: list of arguments
    @type  args: tuple

    @param kwargs: dct of keyword arguments
    @type  kwargs: dict
    """

    channel = None
    target = None

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        self.args = args
        self.kwargs = kwargs

    @property
    def name(self):
        return self.__class__.__name__

    def __eq__(self, other):
        """ x.__eq__(other) <==> x==other

        Tests the equality of Event self against Event y.
        Two Events are considered "equal" iif the name,
        channel and target are identical as well as their
        args and kwargs passed.
        """

        return (self.__class__ is other.__class__
                and self.channel == other.channel
                and self.args == other.args
                and self.kwargs == other.kwargs)

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        if type(self.channel) is tuple:
            channel = "%s:%s" % self.channel
        else:
            channel = self.channel or ""
        return "<%s[%s] %s %s>" % (self.name, channel, self.args, self.kwargs)

    def __getitem__(self, x):
        """x.__getitem__(y) <==> x[y]

        Get and return data from the Event object requested by "x".
        If an int is passed to x, the requested argument from self.args
        is returned index by x. If a str is passed to x, the requested
        keyword argument from self.kwargs is returned keyed by x.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if type(x) is int:
            return self.args[x]
        elif type(x) is str:
            return self.kwargs[x]
        else:
            raise TypeError("Expected int or str, got %r" % type(x))


class Error(Event):
    """Error Event

    This Event is sent for any exceptions that occur during the execution
    of an Event Handler that is not SystemExit or KeyboardInterrupt.

    @param type: type of exception
    @type  type: type

    @param value: exception object
    @type  value: exceptions.TypeError

    @param traceback: traceback of exception
    @type  traceback: traceback

    @param kwargs: (Optional) Additional Information
    @type  kwargs: dict
    """

    channel = "exception"

    def __init__(self, type, value, traceback, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(type, value, traceback, **kwargs)


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

_sortkey = attrgetter("priority", "filter")

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

        return f

    return wrapper

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
        self._globals = []
        self.channels = dict()
        self._cmap = dict()
        self._tmap = dict()

        self._ticks = set()
        self.components = set()

        self._task = None
        self._running = False

        self.root = self
        self.manager = self

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__
        q = len(self._queue)
        c = len(self.channels)
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

    def _getHandlers(self, _channel):
        target, channel = _channel

        channels = self.channels
        exists = self.channels.has_key
        get = self.channels.get
        tmap = self._tmap.get
        cmap = self._cmap.get

        # Global Channels
        handlers = self._globals
  
        # This channel on all targets
        if channel == "*":
            all = tmap(target, [])
            return chain(handlers, all)

        # Every channel on this target
        if target == "*":
            all = cmap(channel, [])
            return chain(handlers, all)

        # Any global channels
        if exists(("*", channel)):
            handlers = chain(handlers, get(("*", channel)))
 
        # Any global channels for this target
        if exists((channel, "*")):
            handlers = chain(handlers, get((channel, "*")))

        # The actual channel and target
        if exists(_channel):
            handlers = chain(handlers, get((_channel)))
  
        return handlers

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def running(self):
        return self._running

    @property
    def state(self):
        if self.running:
            if self._task is None:
                return "R"
            else:
                if self._task.isAlive():
                    return "R"
                else:
                    return "D"
        else:
            return "S"

    def _add(self, handler, channel=None):
        """E._add(handler, channel) -> None

        Add a new Event Handler to the Event Manager
        adding it to the given channel. If no channel is
        given, add it to the global channel.
        """

        if channel is None:
            if handler not in self._globals:
                self._globals.append(handler)
                self._globals.sort(key=_sortkey)
                self._globals.reverse()
        else:
            assert type(channel) is tuple and len(channel) == 2

            self._handlers.add(handler)

            if channel not in self.channels:
                self.channels[channel] = []

            if handler not in self.channels[channel]:
                self.channels[channel].append(handler)
                self.channels[channel].sort(key=_sortkey)
                self.channels[channel].reverse()

            (target, channel) = channel

            if target not in self._tmap:
                self._tmap[target] = []
            if handler not in self._tmap[target]:
                self._tmap[target].append(handler)

            if channel not in self._cmap:
                self._cmap[channel] = []
            if handler not in self._cmap[channel]:
                self._cmap[channel].append(handler)

    def _remove(self, handler, channel=None):
        """E._remove(handler, channel=None) -> None

        Remove the given Event Handler from the Event Manager
        removing it from the given channel. if channel is None,
        remove it from all channels. This will succeed even
        if the specified  handler has already been removed.
        """

        if channel is None:
            if handler in self._globals:
                self._globals.remove(handler)
            channels = self.channels.keys()
        else:
            channels = [channel]

        if handler in self._handlers:
            self._handlers.remove(handler)

        for channel in channels:
            if handler in self.channels[channel]:
                self.channels[channel].remove(handler)
            if not self.channels[channel]:
                del self.channels[channel]

            (target, channel) = channel

            if target in self._tmap and handler in self._tmap:
                self._tmap[target].remove(handler)
                if not self._tmap[target]:
                    del self._tmap[target]

            if channel in self._cmap and handler in self._cmap:
                self._cmap[channel].remove(handler)
                if not self._cmap[channel]:
                    del self._cmap[channel]

    def _push(self, event, channel):
        self._queue.append((event, channel))

    def push(self, event, channel=None, target=None):
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

        channel = channel or event.channel or event.name.lower()
        target = target if target is not None else event.target
        if isinstance(target, Component):
            target = getattr(target, "channel", "*")
        else:
            target = target or getattr(self, "channel", "*")

        event.channel = (target, channel)

        self.root._push(event, (target, channel))

    def _flush(self):
        q = self._queue
        self._queue = deque()
        while q: self._send(*q.popleft())

    def flush(self):
        """Flush all Events in the Event Queue

        This will flush all Events in the Event Queue. If this Component's
        Manager is itself, flush all Events from this Component's Event Queue,
        otherwise, flush all Events from this Component's Manager's Event Queue.
        """

        self.root._flush()

    def _send(self, event, channel, errors=False, log=True):
        eargs = event.args
        ekwargs = event.kwargs

        r = False
        for handler in self._getHandlers(channel):
            try:
                #stime = time.time()
                if handler._passEvent:
                    r = handler(event, *eargs, **ekwargs)
                else:
                    r = handler(*eargs, **ekwargs)
                #etime = time.time()
                #ttime = (etime - stime) * 1e3
                #print "%s: %0.02f ms" % (reprhandler(handler), ttime)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                if log:
                    etype, evalue, etraceback = _exc_info()
                    self.push(Error(etype, evalue, etraceback, handler=handler))
                if errors:
                    raise
                else:
                    _exc_clear()
            if r is not None and r and handler.filter:
                return r
        return r

    def send(self, event, channel=None, target=None, errors=False, log=True):
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

        channel = channel or event.channel or event.name.lower()
        target = target if target is not None else event.target
        if isinstance(target, Component):
            target = getattr(target, "channel", "*")
        else:
            target = target or getattr(self, "channel", "*")

        event.channel = (target, channel)

        return self.root._send(event, (target, channel), errors, log)

    def _signal(self, signal, stack):
        if not self.send(Signal(signal, stack), "signal"):
            if signal == SIGINT:
                raise KeyboardInterrupt
            elif signal == SIGTERM:
                raise SystemExit

    def start(self, sleep=0, log=True, process=False):
        group = None
        target = self.run
        name = self.__class__.__name__
        mode = "P" if process else "T"
        args = (sleep, mode, log,)

        if process and HAS_MULTIPROCESSING:
            args += (self,)
            self._task = Process(group, target, name, args)
            if HAS_MULTIPROCESSING == 2:
                setattr(self._task, "isAlive", self._task.is_alive)
            self._task.start()
            return

        self._task = Thread(group, target, name, args)
        self._task.setDaemon(True)
        self._task.start()

    def join(self, timeout=None):
        if hasattr(self._task, "join"):
            self._task.join(timeout)

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

    def run(self, sleep=0, mode=None, log=True, __self=None):
        if __self is not None:
            self = __self

        if not mode == "T":
            if os.name == "posix":
                signal(SIGHUP, self._signal)
            signal(SIGINT, self._signal)
            signal(SIGTERM, self._signal)

        self._running = True

        self.push(Started(self, mode))

        try:
            while self.running:
                try:
                    [f() for f in self._ticks.copy()]
                    self._flush()
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
                            self.push(Error(*_exc_info()))
                    finally:
                        self._flush()
        finally:
            try:
                self.push(Stopped(self))
                rtime = time.time()
                while len(self) > 0 and (time.time() - rtime) < 3:
                    try:
                        [f() for f in self._ticks.copy()]
                        self._flush()
                        if sleep:
                            time.sleep(sleep)
                        rtime = time.time()
                    except:
                        try:
                            if log:
                                self.push(Error(*_exc_info()))
                        finally:
                            self._flush()
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

    channel = "*"

    def __new__(cls, *args, **kwargs):
        """TODO Work around for Python bug.

        Bug: http://bugs.python.org/issue5322
        """

        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(BaseComponent, self).__init__(*args, **kwargs)

        self.channel = kwargs.get("channel", self.channel) or "*"
        self.register(self)

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__
        channel = self.channel or ""
        q = len(self._queue)
        c = len(self.channels)
        h = len(self._handlers)
        state = self.state
        format = "<%s/%s (q: %d c: %d h: %d) [%s]>"
        return format % (name, channel, q, c, h, state)

    def _registerHandlers(self, manager):
        p = lambda x: callable(x) and getattr(x, "handler", False)
        handlers = [v for k, v in getmembers(self, p)]

        for handler in handlers:
            if handler.channels:
                channels = handler.channels
            else:
                channels = [None]

            for channel in channels:
                if handler.target is not None:
                    target = handler.target
                else:
                    target = getattr(self, "channel", None)
                if not all([channel, target]):
                    channel = None
                else:
                    channel = (target, channel or "*")
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

        def _register(c, m, r):
            c._registerHandlers(m)
            c.root = r
            if c._queue:
                m._queue.extend(list(c._queue))
                c._queue.clear()
            if m is not r:
                c._registerHandlers(r)
                if m._queue:
                    r._queue.extend(list(m._queue))
                    m._queue.clear()
            if hasattr(c, "__tick__"):
                m._ticks.add(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.add(getattr(c, "__tick__"))
            for x in c.components:
                _register(x, m, r)

        _register(self, manager, findroot(manager))

        self.manager = manager

        if manager is not self:
            manager.components.add(self)
            self.push(Registered(self, manager), target=self)

    def unregister(self):
        """Unregister all registered Event Handlers
        
        This will unregister all registered Event Handlers of this Component
        from it's registered Component or Manager.

        @note: It's possible to unregister a Component from itself!
        """

        def _unregister(c, m, r):
            c._unregisterHandlers(m)
            c.root = self
            if m is not r:
                c._unregisterHandlers(r)
            if hasattr(c, "__tick__"):
                m._ticks.remove(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.remove(getattr(c, "__tick__"))

            for x in c.components:
                _unregister(x, m, r)

        self.push(Unregistered(self, self.manager), target=self)

        root = findroot(self.manager)
        _unregister(self, self.manager, root)

        self.manager.components.remove(self)
        self.push(Unregistered(self, self.manager), target=self)

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
                for k, v in base.__dict__.items():
                    p1 = callable(v)
                    p2 = getattr(v, "handler", False)
                    predicate = p1 and p2 and not overridden(v)
                    if predicate:
                        name = "%s_%s" % (base.__name__, k)
                        method = new.instancemethod(v, self, cls)
                        setattr(self, name, method)
        return self
