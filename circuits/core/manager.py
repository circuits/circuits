# Package:  manager
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Manager

This module definse the Manager class subclasses by component.BaseComponent
"""

import os
import greenlet
from time import sleep
from warnings import warn
from itertools import chain
from threading import Thread
from collections import deque, defaultdict
from inspect import getargspec
from traceback import format_tb
from sys import exc_info as _exc_info

from .events import Event

try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

if os.name == "posix":
    from signal import SIGHUP, SIGINT, SIGTERM
    from signal import signal as _registerSignalHandler
elif os.name in ["nt", "java"]:
    from signal import SIGINT, SIGTERM
    from signal import signal as _registerSignalHandler
else:
    raise RuntimeError("Unsupported platform '%s'" % os.name)

try:
    from multiprocessing import Process
    from multiprocessing import current_process
    HAS_MULTIPROCESSING = 2
except:
    try:
        from processing import Process
        from processing import currentProcess as current_process
        HAS_MULTIPROCESSING = 1
    except:
        HAS_MULTIPROCESSING = 0

from greenlet import greenlet

from .values import Value
from .events import Started, Stopped, Signal
from .events import Error, Success, Failure, Filter, Start, End

TIMEOUT = 0.01 # 10ms timeout when no tick functions to process

class Manager(object):
    """Manager

    This is the base Manager of the BaseComponent which manages an Event Queue,
    a set of Event Handlers, Channels, Tick Functions, Registered and Hidden
    Components, a Task and the Running State.

    :ivar manager: The Manager of this Component or Manager
    """

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self._globals = []
        self._tasks = set()
        self._cmap = dict()
        self._tmap = dict()
        self._queue = deque()
        self.channels = dict()
        self._handlers = set()
        self._handlerattrs = dict()
        self._handler_cache = dict()
        self._active_handlers = defaultdict(list)

        self._ticks = set()

        self._task = None
        self._thread = None
        self._process = None
        self._bridge = None
        self._running = False

        self.root = self.manager = self
        self.components = set()

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__

        if hasattr(self, "channel") and self.channel is not None:
            channel = "/%s" % self.channel 
        else:
            channel = ""

        q = len(self._queue)
        c = len(self.channels)
        h = len(self._handlers)
        state = self.state

        if HAS_MULTIPROCESSING:
            pid = current_process().pid
        else:
            pid = os.getpid()

        if pid:
            id = "%s:%s" % (pid, current_thread().getName())
        else:
            id = current_thread().getName()

        format = "<%s%s %s (queued=%d, channels=%d, handlers=%d) [%s]>"
        return format % (name, channel, id, q, c, h, state)

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

    def _getHandlers(self, _channel):
        if _channel in self._handler_cache:
            return self._handler_cache[_channel]

        target, channel = _channel

        get = self.channels.get
        tmap = self._tmap.get
        cmap = self._cmap.get

        def _sortkey(handler):
            return (self._handlerattrs[handler]["priority"],
                    self._handlerattrs[handler]["filter"])

        # Global Channels
        handlers = self._globals[:]

        # This channel on all targets
        if channel == "*":
            handlers.extend(tmap(target, []))
            handlers.sort(key=_sortkey, reverse=True)
            self._handler_cache[_channel] = handlers
            return handlers

        # Every channel on this target
        if target == "*":
            handlers.extend(cmap(channel, []))
            handlers.sort(key=_sortkey, reverse=True)
            self._handler_cache[_channel] = handlers
            return handlers

        # Any global channels
        handlers.extend(get(("*", channel), []))
 
        # Any global channels for this target
        handlers.extend(get((channel, "*"), []))

        # The actual channel and target
        handlers.extend(get(_channel, []))

        handlers.sort(key=_sortkey, reverse=True)
        self._handler_cache[_channel] = handlers
        return handlers

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

        if self.running or (self._task and self._task.isAlive()):
            return "R"
        elif self._task and not self._task.isAlive():
            return "D"
        else:
            return "S"

    def addHandler(self, handler, *channels, **kwargs):
        """Add a new Event Handler

        Add a new Event Handler to the Event Manager.
        """

        self._handler_cache.clear()

        channels = getattr(handler, "channels", channels)

        target = kwargs.get("target", getattr(handler, "target",
            getattr(self, "channel", "*")))

        if isinstance(target, Manager):
            target = getattr(target, "channel", "*")

        attrs = {}
        attrs["channels"] = channels
        attrs["target"] = target

        attrs["filter"] = getattr(handler, "filter",
                kwargs.get("filter", False))
        attrs["priority"] = getattr(handler, "priority",
                kwargs.get("priority", 0))

        if not hasattr(handler, "event"):
            args = getargspec(handler)[0]
            if args and args[0] == "self":
                del args[0]
            attrs["event"] = bool(args and args[0] == "event")
        else:
            attrs["event"] = getattr(handler, "event")

        self._handlerattrs[handler] = attrs

        def _sortkey(handler):
            return (self._handlerattrs[handler]["priority"],
                    self._handlerattrs[handler]["filter"])

        if not channels and target == "*":
            if handler not in self._globals:
                self._globals.append(handler)
                self._globals.sort(key=_sortkey, reverse=True)
        else:
            for channel in channels:
                self._handlers.add(handler)

                if (target, channel) not in self.channels:
                    self.channels[(target, channel)] = []

                if handler not in self.channels[(target, channel)]:
                    self.channels[(target, channel)].append(handler)
                    self.channels[(target, channel)].sort(key=_sortkey,
                            reverse=True)

                if target not in self._tmap:
                    self._tmap[target] = []
                if handler not in self._tmap[target]:
                    self._tmap[target].append(handler)

                if channel not in self._cmap:
                    self._cmap[channel] = []
                if handler not in self._cmap[channel]:
                    self._cmap[channel].append(handler)

    def add(self, *args, **kwargs):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`addHandler` instead.
        """

        warn(DeprecationWarning("Use .addHandler(...) instead"))

        return self.addHandler(*args, **kwargs)


    def removeHandler(self, handler, channel=None):
        """Remove an Event Handler

        Remove the given Event Handler from the Event Manager
        removing it from the given channel. if channel is None,
        remove it from all channels. This will succeed even
        if the specified  handler has already been removed.
        """

        self._handler_cache.clear()

        if channel is None:
            if handler in self._globals:
                self._globals.remove(handler)
            channels = list(self.channels.keys())
        else:
            channels = [channel]

        if handler in self._handlers:
            self._handlers.remove(handler)

        if handler in self._handlerattrs:
            del self._handlerattrs[handler]

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

    def remove(self, *args, **kwargs):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`removeHandler` instead.
        """

        warn(DeprecationWarning("Use .removeHandler(...) instead"))

        self.removeHandler(*args, **kwargs)


    def _fire(self, event, channel):
        self._queue.append((event, channel))

    def fireEvent(self, event, channel=None, target=None):
        """Fire/Push a new Event into the system (queue)

        This will push the given Event, Channel and Target onto the
        Event Queue for later processing.

        if target is None, then target will be set as the Channel of
        the current Component, self.channel (defaulting back to None).

        If this Component's Manager is itself, enqueue on this Component's
        Event Queue, otherwise enqueue on this Component's Manager.

        :param event: The Event Object
        :type  event: Event

        :param channel: The Channel this Event is bound for
        :type  channel: str

        @keyword target: The target Component's channel this Event is bound for
        :type    target: str or Component
        """

        if channel is None and target is None:
            if isinstance(event.channel, tuple):
                target, channel = event.channel
            else:
                channel = event.channel or event.name.lower()
                target = event.target or None
        else:
            channel = channel or event.channel or event.name.lower()

        if isinstance(target, Manager):
            target = getattr(target, "channel", "*")
        else:
            target = target or event.target or getattr(self, "channel", "*")

        event.channel = (target, channel)

        event.value = Value(event, self)

        if event.start is not None:
            self.fire(Start(event), *event.start)

        self.root._fire(event, (target, channel))

        return event.value

    fire = fireEvent

    def push(self, *args, **kwargs):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`fire` instead.
        """

        warn(DeprecationWarning("Use .fire(...) instead"))

        return self.fire(*args, **kwargs)

    def registerTask(self, g):
        self._tasks.add(g)

    def unregisterTask(self, g):
        self._tasks.remove(g)

    def waitEvent(self, cls, limit=None):
        if self._thread and self._thread != current_thread():
            raise Exception('You must be in the manager thread to use waitEvent')
        if self._process and self._process != current_process():
            raise Exception('You must be in the manager process to use waitEvent')

        g = greenlet.getcurrent()

        is_instance = isinstance(cls, Event)
        i = 0
        e = None

        self.registerTask(g)
        try:
            while e != cls if is_instance else e.__class__ != cls:
                if limit and i == limit or self._task is None:
                    return
                e = self._task.switch()
                i += 1
        finally:
            self.unregisterTask(g)

        return e

    wait = waitEvent

    def callEvent(self, event, channel=None, target=None):
        self.fire(event, channel, target)
        e = self.waitEvent(event)
        return e.value.value

    call = callEvent


    def _flush(self):
        q = self._queue
        self._queue = deque()

        for event, channel in q:
            g = greenlet(self._dispatcher)
            g.switch(event, channel)

            for task in self._tasks:
                task.switch(event)

    def flushEvents(self):
        """Flush all Events in the Event Queue

        This will flush all Events in the Event Queue. If this Component's
        Manager is itself, flush all Events from this Component's Event Queue,
        otherwise, flush all Events from this Component's Manager's Event Queue.
        """

        self.root._flush()

    flush = flushEvents

    def _dispatcher(self, event, channel):
        eargs = event.args
        ekwargs = event.kwargs

        retval = None
        handler = None

        for handler in self._getHandlers(channel):
            error = None

            attrs = self._handlerattrs[handler]
            event.handler = handler

            try:
                if attrs["event"]:
                    retval = handler(event, *eargs, **ekwargs)
                else:
                    retval = handler(*eargs, **ekwargs)
                event.value.value = retval
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                etype, evalue, etraceback = _exc_info()
                traceback = format_tb(etraceback)
                error = (etype, evalue, traceback)

                event.value.errors = True

                event.value.value = error

                if event.failure is not None:
                    self.fire(Failure(event, handler, error), *event.failure)
                else:
                    self.fire(Error(etype, evalue, traceback, handler))

            if retval and attrs["filter"]:
                if event.filter is not None:
                    self.fire(Filter(event, handler, retval), *event.filter)
                return # Filter

            if error is None and event.success is not None:
                self.fire(Success(event, handler, retval), *event.success)

        if event.end is not None:
            self.fire(End(event, handler, retval), *event.end)


    def _signalHandler(self, signal, stack):
        self.fire(Signal(signal, stack))
        if signal in [SIGINT, SIGTERM]:
            self.stop()

    def start(self, log=True, link=None, process=False):
        group = None
        target = self.run
        name = self.__class__.__name__
        mode = "P" if process else "T"
        args = (log, mode,)

        if process and HAS_MULTIPROCESSING:
            if link is not None and isinstance(link, Manager):
                from circuits.net.sockets import Pipe
                from circuits.core.bridge import Bridge
                from circuits.core.utils import findroot
                root = findroot(link)
                parent, child = Pipe()
                self._bridge = Bridge(root, socket=parent)
                self._bridge.start()
                args += (child,)

            self._process = Process(group, target, name, args)
            self._process.daemon = True
            self.tick()
            self._process.start()
            return

        self._thread = Thread(group, target, name, args)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop(self):
        self._running = False
        self.fire(Stopped(self))
        if self._process and self._process.is_alive() \
                and not current_process() == self._process:
            self._process.terminate()
        if (self._bridge is not None):
            self._bridge = None
        self._process = None
        self._thread = None
        self._task = None
        self.tick()

    def tick(self):
        if self._ticks:
            try:
                [f() for f in self._ticks.copy()]
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                etype, evalue, etraceback = _exc_info()
                self.fire(Error(etype, evalue, format_tb(etraceback)))
        else:
            sleep(TIMEOUT) # Nothing to do - Let's not tie up the CUP

        self._flush()

    def run(self, *args, **kwargs):
        log = kwargs.get("kwargs", True)
        __mode = kwargs.get("__mode", None)
        __socket = kwargs.get("__socket", None)

        self._task = greenlet(self._run)
        self._task.switch(log, __mode, __socket)

    def _run(self, log, __mode, __socket):
        if current_thread().getName() == "MainThread":
            if os.name == "posix":
                _registerSignalHandler(SIGHUP, self._signalHandler)
            try:
                _registerSignalHandler(SIGINT, self._signalHandler)
                _registerSignalHandler(SIGTERM, self._signalHandler)
            except ValueError:
                pass # Ignore if we can't install signal handlers

        if __socket is not None:
            from circuits.core.bridge import Bridge
            manager = Manager()
            bridge = Bridge(manager, socket=__socket)
            self.register(manager)
            manager.start()

        self._running = True

        self.fire(Started(self, __mode))

        try:
            while self or self.running:
                self.tick()
        finally:
            if __socket is not None:
                while bridge or manager: pass
                manager.stop()
                bridge.stop()
            self.stop()
