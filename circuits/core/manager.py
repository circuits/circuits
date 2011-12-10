# Package:  manager
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Manager

This module definse the Manager class subclasses by component.BaseComponent
"""

import atexit
from time import sleep
from warnings import warn
from itertools import chain
from types import MethodType
from collections import deque
from traceback import format_tb
from sys import exc_info as _exc_info
from signal import signal, SIGINT, SIGTERM
from inspect import getmembers, isfunction
from threading import current_thread, Thread
from multiprocessing import current_process, Process

try:
    from greenlet import getcurrent as getcurrent_greenlet, greenlet
    GREENLET = True
except ImportError:
    GREENLET = False

from .values import Value
from .events import Success, Failure, End
from .events import Event, Error, Started, Stopped, Signal

TIMEOUT = 0.01  # 10ms timeout when no tick functions to process


class Manager(object):
    """Manager

    This is the base Manager of the BaseComponent which manages an Event Queue,
    a set of Event Handlers, Channels, Tick Functions, Registered and Hidden
    Components, a Task and the Running State.

    :ivar manager: The Manager of this Component or Manager
    """

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self._tasks = set()
        self._cache = dict()
        self._queue = deque()
        self._globals = set()
        self._handlers = dict()

        self._ticks = None

        self._task = None
        self._running = False

        if GREENLET:
            self._greenlet = None

        self.root = self.parent = self
        self.components = set()

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__

        if hasattr(self, "channel") and self.channel is not None:
            channel = "/%s" % self.channel
        else:
            channel = ""

        q = len(self._queue)
        state = self.state

        pid = current_process().pid

        if pid:
            id = "%s:%s" % (pid, current_thread().getName())
        else:
            id = current_thread().getName()

        format = "<%s%s %s (queued=%d) [%s]>"
        return format % (name, channel, id, q, state)

    def __contains__(self, y):
        """x.__contains__(y) <==> y in x

        Return True if the Component y is registered.
        """

        components = self.components.copy()
        return y in components or y in [c.__class__ for c in components]

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

        if y.manager is not y:
            y.unregister()
        return self

    def __isub__(self, y):
        """x.__sub__(y) <==> x -= y

        (Optional) Convenience operator to unregister y from x
        Equivalent to: y.unregister()

        @return: x
        @rtype Component or Manager
        """

        if y.manager is not y:
            y.unregister()
        return self

    @property
    def name(self):
        """Return the name of this Component/Manager"""

        return self.__class__.__name__

    @property
    def running(self):
        """Return the running state of this Component/Manager"""

        return self._running

    @property
    def state(self):
        """Return the current state of this Component/Manager

        The state can be one of:
         - [R]unning
         - [D]ead
         - [S]topped
        """

        if self.running or (self._task and self._task.is_alive()):
            return "R"
        elif self._task and not self._task.is_alive():
            return "D"
        else:
            return "S"

    def getHandlers(self, event, channel):
        channel_is_instance = isinstance(channel, Manager)
        if channel_is_instance and channel != self:
            return channel.getHandlers(event, channel)

        name = event.name
        handlers = set()

        handlers_chain = [self._handlers.get("*", set())]

        if name in self._handlers:
            handlers_chain.append(self._handlers[name])

        for handler in chain(*handlers_chain):
            if handler.channel:
                handler_channel = handler.channel
            elif hasattr(handler, "__self__"):
                handler_channel = getattr(handler.__self__, "channel", None)
            else:
                handler_channel = None

            if channel == "*" or handler_channel in ("*", channel,) \
                    or channel_is_instance:
                handlers.add(handler)

        handlers.update(self._globals)

        if not channel_is_instance:
            for c in self.components.copy():
                handlers.update(c.getHandlers(event, channel))

        return handlers

    def addHandler(self, f):
        if isfunction(f):
            method = MethodType(f, self, self.__class__)
        else:
            method = f

        setattr(self, method.__name__, method)

        if not method.names and method.channel == "*":
            self._globals.add(f)
        elif not method.names:
            self._handlers.setdefault("*", set()).add(method)
        else:
            for name in method.names:
                self._handlers.setdefault(name, set()).add(method)

        self.root._cache.clear()

    def removeHandler(self, f, event=None):
        if isfunction(f):
            method = MethodType(f, self, self.__class__)
        else:
            method = f

        if event is None:
            names = method.names
        else:
            names = [event]

        for name in names:
            self._handlers[name].remove(method)
            if not self._handlers[name]:
                delattr(self, method.__name__)

        self.root._cache.clear()

    def registerChild(self, component):
        self.components.add(component)
        self.root._queue.extend(list(component._queue))
        component._queue.clear()
        self.root._cache.clear()
        self.root._ticks = None

    def unregisterChild(self, component):
        self.components.remove(component)
        self.root._cache.clear()
        self.root._ticks = None

    def _fire(self, event, channel):
        self._queue.append((event, channel))

    def fireEvent(self, event, *channels):
        """Fire an event into the system

        ...
        """

        if not channels:
            channels = (getattr(self, "channel", "*") or "*",)

        event.channels = channels

        event.value = Value(event, self, getattr(event, 'notify', False))
        self.root._fire(event, channels)

        return event.value

    fire = fireEvent

    def registerTask(self, g):
        self._tasks.add(g)

    def unregisterTask(self, g):
        self._tasks.remove(g)

    def waitEvent(self, cls, limit=None):
        if self._task is not None  and self._task not in [current_process(),
                current_thread()]:
            raise Exception((
                "Cannot use .waitEvent from other threads or processes"
            ))

        g = getcurrent_greenlet()

        is_instance = isinstance(cls, Event)
        i = 0
        e = None
        caller = self._greenlet

        self.registerTask(g)
        try:
            while e != cls if is_instance else e.__class__ != cls:
                if limit and i == limit or self._task is None:
                    return
                e, caller = caller.switch()
                i += 1
        finally:
            self.unregisterTask(g)

        return e

    wait = waitEvent

    def callEvent(self, event, channel="*"):
        self.fire(event, channel)
        e = self.waitEvent(event)
        return e.value

    call = callEvent

    def _flush(self):
        q = self._queue
        self._queue = deque()

        if GREENLET:
            for event, channels in q:
                dispatcher = greenlet(self._dispatcher)
                dispatcher.switch(event, channels)
        else:
            for event, channels in q:
                self._dispatcher(event, channels)

    def flushEvents(self):
        """Flush all Events in the Event Queue"""

        self.root._flush()

    flush = flushEvents

    def _dispatcher(self, event, channels):
        eargs = event.args
        ekwargs = event.kwargs

        def _sortkey(handler):
            return (handler.priority, handler.filter)

        if (event.name, channels) in self._cache:
            handlers = self._cache[(event.name, channels)]
        else:
            h = (self.getHandlers(event, channel) for channel in channels)
            handlers = sorted(chain(*h), key=_sortkey, reverse=True)
            self._cache[(event.name, channels)] = handlers

        error = None

        for handler in handlers:
            event.handler = handler
            try:
                if handler.event:
                    value = handler(event, *eargs, **ekwargs)
                else:
                    value = handler(*eargs, **ekwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                etype, evalue, etraceback = _exc_info()
                traceback = format_tb(etraceback)
                error = (etype, evalue, traceback)

                event.value.errors = True

                value = error

                if event.failure:
                    self.fire(Failure.create("%sFailure" %
                        event.__class__.__name__, event))
                self.fire(Error(etype, evalue, traceback, handler))

            event.value.value = value

            if value and handler.filter:
                break

        if error is None and event.success:
            self.fire(Success.create("%sSuccess" %
                event.__class__.__name__, event))

        if event.end:
            self.fire(End.create("%sEnd" % event.__class__.__name__, event))

        if GREENLET:
            for task in self._tasks.copy():
                task.switch(event, getcurrent_greenlet())

    def _signalHandler(self, signal, stack):
        self.fire(Signal(signal, stack))
        if signal in [SIGINT, SIGTERM]:
            self.stop()

    def start(self, process=False):
        Task = Process if process else Thread

        self._task = Task(target=self.run, name=self.name)

        self._task.daemon = True
        self._task.start()

    def stop(self):
        if not self.running:
            return

        self._running = False
        self.fire(Stopped(self))

        for _ in range(3):
            self.tick()

        self._task = None

    def getTicks(self):
        ticks = set()

        def is_tick(f):
            return callable(f) and getattr(f, 'tick', False) is True

        for k, v in getmembers(self, is_tick):
            ticks.add(v)

        # Kept for backward compatibility
        if getattr(self, '__tick__', False):
            ticks.add(self.__tick__)

        for c in self.components.copy():
            ticks.update(c.getTicks())

        return ticks

    def tick(self):
        if self._ticks is None:
            self._ticks = self.getTicks()

        for f in self._ticks.copy():
            try:
                f()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                etype, evalue, etraceback = _exc_info()
                self.fire(Error(etype, evalue, format_tb(etraceback)))

        if self:
            self.flush()
        else:
            sleep(TIMEOUT)

    def run(self):
        if GREENLET:
            self._greenlet = greenlet(self._run)
            self._greenlet.switch()
        else:
            self._run()

    def _run(self):
        atexit.register(self.stop)

        if current_thread().getName() == "MainThread":
            try:
                signal(SIGINT,  self._signalHandler)
                signal(SIGTERM, self._signalHandler)
            except ValueError:
                # Ignore if we can't install signal handlers
                pass

        self._running = True

        self.fire(Started(self))

        try:
            while self or self.running:
                self.tick()
        finally:
            self.tick()
