# Package:  manager
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Manager

This module definse the Manager class subclasses by component.BaseComponent
"""

from time import sleep
from warnings import warn
from collections import deque
from inspect import getargspec
from traceback import format_tb
from sys import exc_info as _exc_info
from signal import signal, SIGINT, SIGTERM
from threading import current_thread, Thread
from multiprocessing import current_process, Process

from .values import Value
from .events import Event, Started, Stopped, Signal
from .events import Error, Success, Failure, Filter, Start, End

TIMEOUT = 0.01  # 10ms timeout when no tick functions to process

try:
    from greenlet import getcurrent as getcurrent_greenlet, greenlet
    class BaseManager(object):
        def waitEvent(self, cls, limit=None):
            if self._thread and self._thread != current_thread():
                raise Exception("Cannot use .waitEvent from other thread")
            if self._proc and self._proc != current_process():
                raise Exception("Cannot use .waitEvent from other process")

            g = getcurrent_greenlet()

            is_instance = isinstance(cls, Event)
            i = 0
            e = None
            caller = self._task

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

        def callEvent(self, event, target=None, channel=None):
            self.fire(event, target, channel)
            e = self.waitEvent(event)
            return e.value

        call = callEvent

        def run(self, *args, **kwargs):
            log = kwargs.get("log", True)
            __mode = kwargs.get("__mode", None)
            __socket = kwargs.get("__socket", None)

            self._task = greenlet(self._run)
            self._task.switch(log, __mode, __socket)

        def _flush(self):
            q = self._queue
            self._queue = deque()

            for event, channel in q:
                dispatcher = greenlet(self._dispatcher)
                dispatcher.switch(event, channel)

                for task in self._tasks.copy():
                    task.switch(event, getcurrent_greenlet())

except ImportError:
    class BaseManager(object):
        def _flush(self):
            q = self._queue
            self._queue = deque()

            for event, channel in q:
                self._dispatcher(event, channel)

        def run(self, *args, **kwargs):
            log = kwargs.get("log", True)
            __mode = kwargs.get("__mode", None)
            __socket = kwargs.get("__socket", None)

            self._run(log, __mode, __socket)



class Manager(BaseManager):
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
        self._events = dict()

        self._ticks = set()

        self._task = None
        self._thread = None
        self._proc = None
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

        pid = current_process().pid

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

        def _sortkey(handler):
            return (handler.priority, handler.filter)

        # Global Channels
        handlers = set(self._globals)

        # The actual channel and target
        if isinstance(target, Manager):
            handler = getattr(target, channel, None)
            if handler and hasattr(handler, "handler"):
                handlers.add(handler)
        else:
            handlers.update(self._events.get(channel, []))

        print 'target: %s' % str(target)
        print 'channel: %s' % str(channel)
        print 'handlers: %s' % str(handlers)
        print 'globals: %s' % str(self._globals)
        #if channel == 'unregister':
        #    import os
        #    os._exit(1)

        handlers = sorted(handlers, key=_sortkey, reverse=True)
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

        print 'addHandler: %s on %s' % (handler, channels)
        channels = getattr(handler, "channels", channels)

        target = kwargs.get("target", getattr(handler, "target",
            getattr(self, "channel", "*")))

        def _sortkey(handler):
            return (handler.priority, handler.filter)

        if "*" in channels and target == "*":
            if handler not in self._globals:
                print 'registering global %s on %s' % (handler, self)
                self._globals.append(handler)
                self._globals.sort(key=_sortkey, reverse=True)
        else:
            self._handlers.add(handler)
            for channel in channels:

                if channel not in self._events:
                    self._events[channel] = []

                if handler not in self._events[channel]:
                    self._events[channel].append(handler)
                    self._events[channel].sort(key=_sortkey,
                            reverse=True)

    def add(self, *args, **kwargs):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`addHandler` instead.
        """

        warn(DeprecationWarning("Use .addHandler(...) instead"))

        return self.addHandler(*args, **kwargs)

    def removeHandler(self, handler, channels=[]):
        """Remove an Event Handler

        Remove the given Event Handler from the Event Manager
        removing it from the given channel. if channel is None,
        remove it from all channels. This will succeed even
        if the specified  handler has already been removed.
        """

        self._handler_cache.clear()

        channels = getattr(handler, "channels", channels)
        print 'removing handler: %s on %s' % (handler, channels)


        if handler in self._handlers:
            self._handlers.remove(handler)

        for channel in channels:
            if channel == '*' and handler in self._globals:
                self._globals.remove(handler)

            if handler in self._events[channel]:
                self._events[channel].remove(handler)
            if not self._events[channel]:
                del self._events[channel]



    def remove(self, *args, **kwargs):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`removeHandler` instead.
        """

        warn(DeprecationWarning("Use .removeHandler(...) instead"))

        self.removeHandler(*args, **kwargs)

    def _fire(self, event, channel):
        self._queue.append((event, channel))

    def fireEvent(self, event, target=None, channel=None):
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
                target = event.target or getattr(self, "channel", "*")
        elif isinstance(target, Manager):
            channel = channel or event.channel or event.name.lower()
        elif channel is None and '.' in target:
            if target[-1] == '.':
                channel = channel or event.channel or event.name.lower()
                target = target[:-1]
            else:
                target, channel = target.split('.')
        elif channel is None:
            channel = target
            target = getattr(self, "channel", "*")

        event.channel = (target, channel)

        event.value = Value(event, self)

        if event.start is not None:
            self.push(Start(event), *event.start)

        self.root._fire(event, (target, channel))

        return event.value

    fire = fireEvent

    def push(self, event, channel=None, target=None):
        """Deprecated in 1.6

        .. deprecated:: 1.6
           Use :py:meth:`fire` instead.
        """

        warn(DeprecationWarning("Use .fire(...) instead"))

        if not target:
            target = channel
            channel = None
        return self.fire(event, target, channel)

    def registerTask(self, g):
        self._tasks.add(g)

    def unregisterTask(self, g):
        self._tasks.remove(g)

    def flushEvents(self):
        """Flush all Events in the Event Queue"""

        self.root._flush()

    flush = flushEvents

    def _dispatcher(self, event, channel):
        eargs = event.args
        ekwargs = event.kwargs

        retval = None
        handler = None

        handlers = self._getHandlers(channel)
        print '=======> fetched %s handlers: %s' % (channel, str(handlers))
        for handler in handlers:
            print 'handling: %s' % handler
            error = None
            event.handler = handler

            try:
                if handler.event:
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
                    self.push(Failure(event, handler, error), *event.failure)
                else:
                    self.fire(Error(etype, evalue, traceback, handler))

            if retval and handler.filter:
                if event.filter is not None:
                    self.push(Filter(event, handler, retval), *event.filter)
                return  # Filter

            if error is None and event.success is not None:
                self.push(Success(event, handler, retval), *event.success)

        if event.end is not None:
            self.push(End(event, handler, retval), *event.end)

    def _signalHandler(self, signal, stack):
        self.fire(Signal(signal, stack))
        if signal in [SIGINT, SIGTERM]:
            self.stop()

    def start(self, log=True, link=None, process=False):
        group = None
        target = self.run
        name = self.__class__.__name__
        mode = "P" if process else "T"
        args = ()
        kwargs = {'log': log, '__mode': mode}

        if process:
            if link is not None and isinstance(link, Manager):
                from circuits.net.sockets import Pipe
                from circuits.core.bridge import Bridge
                from circuits.core.utils import findroot
                root = findroot(link)
                parent, child = Pipe()
                self._bridge = Bridge(root, socket=parent)
                self._bridge.start()
                kwargs['__socket'] = child

            self._proc = Process(group, target, name, args, kwargs)
            self._proc.daemon = True
            self.tick()
            self._proc.start()
            return

        self._thread = Thread(group, target, name, args, kwargs)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop(self):
        self._running = False
        self.fire(Stopped(self))
        if self._proc and self._proc.is_alive() \
                and not current_process() == self._proc:
            self._proc.terminate()
        if (self._bridge is not None):
            self._bridge = None
        self._process = None
        self._thread = None
        self._task = None
        self.tick()

    def tick(self):
        try:
            [f() for f in self._ticks.copy()]
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            etype, evalue, etraceback = _exc_info()
            self.fire(Error(etype, evalue, format_tb(etraceback)))

        if self:
            self.flush()
        else:
            sleep(TIMEOUT)

    def _run(self, log, __mode, __socket):
        if current_thread().getName() == "MainThread":
            try:
                signal(SIGINT,  self._signalHandler)
                signal(SIGTERM, self._signalHandler)
            except ValueError:
                pass  # Ignore if we can't install signal handlers

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
                while bridge or manager:
                    self.tick()
                manager.stop()
                bridge.stop()
            self.stop()
