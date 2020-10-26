"""
This module defines the Manager class.
"""
import atexit
from collections import deque
from heapq import heappop, heappush
from inspect import isfunction
from itertools import chain, count
from multiprocessing import Process, current_process
from operator import attrgetter
from os import getpid, kill
from signal import SIGINT, SIGTERM, signal as set_signal_handler
from sys import exc_info as _exc_info, stderr
from threading import RLock, Thread, current_thread
from time import time
from traceback import format_exc
from types import GeneratorType
from uuid import uuid4 as uuid

from ..six import Iterator, create_bound_method, next
from ..tools import tryimport
from .events import Event, exception, generate_events, signal, started, stopped
from .handlers import handler
from .values import Value

try:
    from signal import SIGKILL
except ImportError:
    SIGKILL = SIGTERM


thread = tryimport(("thread", "_thread"))


TIMEOUT = 0.1  # 100ms timeout when idle


class UnregistrableError(Exception):

    """Raised if a component cannot be registered as child."""


class TimeoutError(Exception):

    """Raised if wait event timeout occurred"""


class CallValue(object):

    def __init__(self, value):
        self.value = value


class ExceptionWrapper(object):

    def __init__(self, exception):
        self.exception = exception

    def extract(self):
        return self.exception


class Sleep(Iterator):

    def __init__(self, seconds):
        self._task = None

        try:
            self.expiry = time() + float(seconds)
        except ValueError:
            raise TypeError("a float is required")

    def __iter__(self):
        return self

    def __repr__(self):
        return "sleep({0:s})".format(repr(self.expiry - time()))

    def __next__(self):
        if time() >= self.expiry:
            raise StopIteration()
        return self

    @property
    def expired(self):
        return time() >= self.expiry

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task


def sleep(seconds):
    """
    Delay execution of a coroutine for a given number of seconds.
    The argument may be a floating point number for subsecond precision.
    """

    return Sleep(seconds)


class Dummy(object):

    channel = None


_dummy = Dummy()
del Dummy


class _State(object):

    __slots__ = ('task', 'run', 'flag', 'event', 'timeout', 'parent', 'task_event', 'tick_handler')

    def __init__(self, timeout):
        self.task = None
        self.run = False
        self.flag = False
        self.event = None
        self.timeout = timeout
        self.parent = None
        self.task_event = None
        self.tick_handler = None


class _EventQueue(object):
    __slots__ = ('_queue', '_priority_queue', '_counter', '_flush_batch')

    def __init__(self):
        self._queue = deque()
        self._priority_queue = []
        self._counter = count()
        self._flush_batch = 0

    def __len__(self):
        return len(self._queue) + len(self._priority_queue)

    def drainFrom(self, other_queue):
        self._queue.extend(other_queue._queue)
        other_queue._queue.clear()
        # Queue is currently flushing events /o\
        assert not len(other_queue._priority_queue)

    def append(self, event, channel, priority):
        self._queue.append((priority, next(self._counter), (event, channel)))

    def dispatchEvents(self, dispatcher):
        if self._flush_batch == 0:
            # FIXME: Might be faster to use heapify instead of pop +
            # heappush. Though, with regards to thread safety this
            # appears to be the better approach.
            self._flush_batch = count = len(self._queue)
            while count:
                count -= 1
                heappush(self._priority_queue, self._queue.popleft())

        while self._flush_batch > 0:
            self._flush_batch -= 1  # Decrement first!
            (event, channels) = heappop(self._priority_queue)[2]
            dispatcher(event, channels, self._flush_batch)


class Manager(object):

    """
    The manager class has two roles. As a base class for component
    implementation, it provides methods for event and handler management.
    The method :meth:`.fireEvent` appends a new event at the end of the event
    queue for later execution. :meth:`.waitEvent` suspends the execution
    of a handler until all handlers for a given event have been invoked.
    :meth:`.callEvent` combines the last two methods in a single method.

    The methods :meth:`.addHandler` and :meth:`.removeHandler` allow handlers
    for events to be added and removed dynamically. (The more common way to
    register a handler is to use the :func:`~.handlers.handler` decorator
    or derive the class from :class:`~.components.Component`.)

    In its second role, the :class:`.Manager` takes the role of the
    event executor. Every component hierarchy has a root component that
    maintains a queue of events. Firing an event effectively means
    appending it to the event queue maintained by the root manager.
    The :meth:`.flush` method removes all pending events from the
    queue and, for each event, invokes all the handlers. Usually,
    :meth:`.flush` is indirectly invoked by :meth:`run`.

    The manager optionally provides information about the execution of
    events as automatically generated events. If an :class:`~.events.Event`
    has its :attr:`success` attribute set to True, the manager fires
    a :class:`~.events.Success` event if all handlers have been
    executed without error. Note that this event will be
    enqueued (and dispatched) immediately after the events that have been
    fired by the event's handlers. So the success event indicates both
    the successful invocation of all handlers for the event and the
    processing of the immediate follow-up events fired by those handlers.

    Sometimes it is not sufficient to know that an event and its
    immediate follow-up events have been processed. Rather, it is
    important to know when all state changes triggered by an event,
    directly or indirectly, have been performed. This also includes
    the processing of events that have been fired when invoking
    the handlers for the follow-up events and the processing of events
    that have again been fired by those handlers and so on. The completion
    of the processing of an event and all its direct or indirect
    follow-up events may be indicated by a :class:`~.events.Complete`
    event. This event is generated by the manager if :class:`~.events.Event`
    has its :attr:`complete` attribute set to True.

    Apart from the event queue, the root manager also maintains a list of
    tasks, actually Python generators, that are updated when the event queue
    has been flushed.
    """

    _currently_handling = None
    """
    The event currently being handled.
    """

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        self._queue = _EventQueue()

        self._tasks = set()
        self._cache = dict()
        self._globals = set()
        self._handlers = dict()

        self._flush_batch = 0
        self._cache_needs_refresh = False

        self._executing_thread = None
        self._flushing_thread = None
        self._running = False
        self.__thread = None
        self.__process = None
        self._lock = RLock()

        self.root = self.parent = self
        self.components = set()

    def __nonzero__(self):
        "x.__nonzero__() <==> bool(x)"

        return True

    __bool__ = __nonzero__

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.__class__.__name__

        channel = "/{0:s}".format(str(getattr(self, "channel", "")))

        q = len(self._queue)
        state = "R" if self.running else "S"

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

        (Optional) Convenience operator to unregister y from x.parent
        Equivalent to: y.unregister()

        @return: x
        @rtype Component or Manager
        """

        if y.parent is not y:
            y.unregister()
        return self

    def __isub__(self, y):
        """x.__sub__(y) <==> x -= y

        (Optional) Convenience operator to unregister y from x
        Equivalent to: y.unregister()

        @return: x
        @rtype Component or Manager
        """

        if y.parent is not y:
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
    def pid(self):
        """Return the process id of this Component/Manager"""

        return getpid() if self.__process is None else self.__process.pid

    def getHandlers(self, event, channel, **kwargs):
        name = event.name
        handlers = set()

        _handlers = set()
        _handlers.update(self._handlers.get("*", []))
        _handlers.update(self._handlers.get(name, []))

        for _handler in _handlers:
            handler_channel = _handler.channel
            if handler_channel is None:
                # XXX: Why do we care about the event handler's channel?
                #      This probably costs us performance for what?
                #      I've not ever had to rely on this in practice...
                handler_channel = getattr(
                    getattr(
                        _handler, "im_self", getattr(
                            _handler, "__self__", _dummy
                        )
                    ),
                    "channel", None
                )

            if channel == "*" or handler_channel in ("*", channel,) \
                    or channel is self:
                handlers.add(_handler)

        if not kwargs.get("exclude_globals", False):
            handlers.update(self._globals)

        for c in self.components.copy():
            handlers.update(c.getHandlers(event, channel, **kwargs))

        return handlers

    def addHandler(self, f):
        method = create_bound_method(f, self) if isfunction(f) else f

        setattr(self, method.__name__, method)

        if not method.names and method.channel == "*":
            self._globals.add(method)
        elif not method.names:
            self._handlers.setdefault("*", set()).add(method)
        else:
            for name in method.names:
                self._handlers.setdefault(name, set()).add(method)

        self.root._cache_needs_refresh = True

        return method

    def removeHandler(self, method, event=None):
        if event is None:
            names = method.names
        else:
            names = [event]

        for name in names:
            self._handlers[name].remove(method)
            if not self._handlers[name]:
                del self._handlers[name]
                try:
                    delattr(self, method.__name__)
                except AttributeError:
                    # Handler was never part of self
                    pass

        self.root._cache_needs_refresh = True

    def registerChild(self, component):
        if component._executing_thread is not None:
            if self.root._executing_thread is not None:
                raise UnregistrableError()
            self.root._executing_thread = component._executing_thread
            component._executing_thread = None
        self.components.add(component)
        self.root._queue.drainFrom(component._queue)
        self.root._cache_needs_refresh = True

    def unregisterChild(self, component):
        self.components.remove(component)
        self.root._cache_needs_refresh = True

    def _fire(self, event, channel, priority=0):
        # check if event is fired while handling an event
        th = (self._executing_thread or self._flushing_thread)
        if thread.get_ident() == (th.ident if th else None) and \
                not isinstance(event, signal):
            if self._currently_handling is not None and \
                    getattr(self._currently_handling, "cause", None):
                # if the currently handled event wants to track the
                # events generated by it, do the tracking now
                event.cause = self._currently_handling
                event.effects = 1
                self._currently_handling.effects += 1

            self._queue.append(event, channel, priority)

        # the event comes from another thread
        else:
            # Another thread has provided us with something to do.
            # If the component is running, we must make sure that
            # any pending generate event waits no longer, as there
            # is something to do now.
            with self._lock:
                # Modifications of attribute self._currently_handling
                # (in _dispatch()), calling reduce_time_left(0). and adding an
                # event to the (empty) event queue must be atomic, so we have
                # to lock. We can save the locking around
                # self._currently_handling = None though, but then need to copy
                # it to a local variable here before performing a sequence of
                # operations that assume its value to remain unchanged.
                handling = self._currently_handling

                self._queue.append(event, channel, priority)
                if isinstance(handling, generate_events):
                    handling.reduce_time_left(0)

    def fireEvent(self, event, *channels, **kwargs):
        """Fire an event into the system.

        :param event: The event that is to be fired.
        :param channels: The channels that this event is delivered on.
           If no channels are specified, the event is delivered to the
           channels found in the event's :attr:`channel` attribute.
           If this attribute is not set, the event is delivered to
           the firing component's channel. And eventually,
           when set neither, the event is delivered on all
           channels ("*").
        """

        if not channels:
            channels = event.channels or (getattr(self, "channel", "*"),) or ("*",)

        event.channels = channels

        event.value = Value(event, self)
        self.root._fire(event, channels, **kwargs)

        return event.value

    fire = fireEvent

    def registerTask(self, g):
        self.root._tasks.add(g)

    def unregisterTask(self, g):
        if g in self.root._tasks:
            self.root._tasks.remove(g)

    def waitEvent(self, event, *channels, **kwargs):  # noqa
        # XXX: C901: This has a high McCabe complexity score of 16.
        # TODO: Refactor this method.

        if isinstance(event, Event):
            event_object = event
            event_name = event.name
            channels = event.channels or channels
        else:
            event_object = None
            event_name = event

        state = _State(timeout=kwargs.get("timeout", -1))

        def _on_event(self, event, *args, **kwargs):
            if not state.run and (
                    event_object is None or event is event_object
            ):
                self.removeHandler(_on_event_handler, event_name)
                event.alert_done = True
                state.run = True
                state.event = event

        def _on_done(self, event, *args, **kwargs):
            if state.event == event.parent:
                state.flag = True
                self.registerTask((state.task_event, state.task, state.parent))
                if state.timeout > 0:
                    self.removeHandler(state.tick_handler, "generate_events")

        def _on_tick(self):
            if state.timeout == 0:
                self.registerTask(
                    (
                        state.task_event,
                        (e for e in (ExceptionWrapper(TimeoutError()),)),
                        state.parent
                    )
                )
                self.removeHandler(_on_done_handler, "%s_done" % event_name)
                self.removeHandler(_on_tick_handler, "generate_events")
            elif state.timeout > 0:
                state.timeout -= 1

        if not channels:
            channels = (None,)

        for channel in channels:
            _on_event_handler = self.addHandler(
                handler(event_name, channel=channel)(_on_event))
            _on_done_handler = self.addHandler(
                handler("%s_done" % event_name, channel=channel)(_on_done))
            if state.timeout >= 0:
                _on_tick_handler = state.tick_handler = self.addHandler(
                    handler("generate_events", channel=channel)(_on_tick))

        yield state

        self.removeHandler(_on_done_handler, "%s_done" % event_name)

        if state.event is not None:
            yield CallValue(state.event.value)

    wait = waitEvent

    def callEvent(self, event, *channels, **kwargs):
        """
        Fire the given event to the specified channels and suspend
        execution until it has been dispatched. This method may only
        be invoked as argument to a ``yield`` on the top execution level
        of a handler (e.g. "``yield self.callEvent(event)``").
        It effectively creates and returns a generator
        that will be invoked by the main loop until the event has
        been dispatched (see :func:`circuits.core.handlers.handler`).
        """
        value = self.fire(event, *channels)
        for r in self.waitEvent(event, *event.channels, **kwargs):
            yield r
        yield CallValue(value)

    call = callEvent

    def _flush(self):
        # Handle events currently on queue, but none of the newly generated
        # events. Note that _flush can be called recursively.
        old_flushing = self._flushing_thread
        try:
            self._flushing_thread = current_thread()
            self._queue.dispatchEvents(self._dispatcher)
        finally:
            self._flushing_thread = old_flushing

    def flushEvents(self):
        """
        Flush all Events in the Event Queue. If called on a manager
        that is not the root of an object hierarchy, the invocation
        is delegated to the root manager.
        """

        self.root._flush()

    flush = flushEvents

    def _dispatcher(self, event, channels, remaining):  # noqa
        # XXX: C901: This has a high McCabe complexity score of 22.
        # TODO: Refactor this method.

        if event.cancelled:
            return

        if event.complete:
            if not getattr(event, "cause", None):
                event.cause = event
            event.effects = 1  # event itself counts (must be done)
        eargs = event.args
        ekwargs = event.kwargs

        if self._cache_needs_refresh:
            # Don't call self._cache.clear() from other threads,
            # this may interfere with cache rebuild.
            self._cache.clear()
            self._cache_needs_refresh = False
        try:  # try/except is fastest if successful in most cases
            event_handlers = self._cache[(event.name, channels)]
        except KeyError:
            h = (self.getHandlers(event, channel) for channel in channels)

            event_handlers = sorted(
                chain(*h),
                key=attrgetter("priority"),
                reverse=True
            )

            if isinstance(event, generate_events):
                from .helpers import FallBackGenerator
                event_handlers.append(FallBackGenerator()._on_generate_events)
            elif isinstance(event, exception) and len(event_handlers) == 0:
                from .helpers import FallBackExceptionHandler
                event_handlers.append(FallBackExceptionHandler()._on_exception)
            elif isinstance(event, signal) and len(event_handlers) == 0:
                from .helpers import FallBackSignalHandler
                event_handlers.append(FallBackSignalHandler()._on_signal)

            self._cache[(event.name, channels)] = event_handlers

        if isinstance(event, generate_events):
            with self._lock:
                self._currently_handling = event
                if remaining > 0 or len(self._queue) or not self._running:
                    event.reduce_time_left(0)
                elif self._tasks:
                    event.reduce_time_left(TIMEOUT)
                # From now on, firing an event will reduce time left
                # to 0, which prevents event handlers from waiting (or wakes
                # them up with resume if they should be waiting already)
        else:
            self._currently_handling = event

        value = None
        err = None

        for event_handler in event_handlers:
            event.handler = event_handler
            try:
                if event_handler.event:
                    value = event_handler(event, *eargs, **ekwargs)
                else:
                    value = event_handler(*eargs, **ekwargs)
            except KeyboardInterrupt:
                self.stop()
            except SystemExit as e:
                self.stop(e.code)
            except BaseException:
                value = err = _exc_info()
                event.value.errors = True

                if event.failure:
                    self.fire(
                        event.child("failure", event, err),
                        *event.channels
                    )

                self.fire(exception(*err, handler=event_handler, fevent=event))

            if value is not None:
                if isinstance(value, GeneratorType):
                    event.waitingHandlers += 1
                    event.value.promise = True
                    self.registerTask((event, value, None))
                else:
                    event.value.value = value

            # it is kind of a temporal hack to allow processing
            # of tasks, added in one of event handlers here
            if isinstance(event, generate_events) and self._tasks:
                event.reduce_time_left(TIMEOUT)

            if event.stopped:
                break  # Stop further event processing

        self._currently_handling = None
        self._eventDone(event, err)

    def _eventDone(self, event, err=None):
        if event.waitingHandlers:
            return

        # The "%s_done" event is for internal use by waitEvent only.
        # Use the "%s_success" event in your application if you are
        # interested in being notified about the last handler for
        # an event having been invoked.
        if event.alert_done:
            self.fire(event.child("done", event.value.value), *event.channels)

        if err is None and event.success:
            channels = getattr(event, "success_channels", event.channels)
            self.fire(
                event.child("success", event, event.value.value), *channels
            )

        while True:
            # cause attributes indicates interest in completion event
            cause = getattr(event, "cause", None)
            if not cause:
                break
            # event takes part in complete detection (as nested or root event)
            event.effects -= 1
            if event.effects > 0:
                break  # some nested events remain to be completed
            if event.complete:  # does this event want signaling?
                self.fire(
                    event.child("complete", event, event.value.value),
                    *getattr(event, "complete_channels", event.channels)
                )

            # this event and nested events are done now
            delattr(event, "cause")
            delattr(event, "effects")
            # cause has one of its nested events done, decrement and check
            event = cause

    def _signal_handler(self, signo, stack):
        self.fire(signal(signo, stack))

    def start(self, process=False, link=None):
        """
        Start a new thread or process that invokes this manager's
        ``run()`` method. The invocation of this method returns
        immediately after the task or process has been started.
        """

        if process:
            # Parent<->Child Bridge
            if link is not None:
                from circuits.net.sockets import Pipe
                from circuits.core.bridge import Bridge

                channels = (uuid(),) * 2
                parent, child = Pipe(*channels)
                bridge = Bridge(parent, channel=channels[0]).register(link)

                args = (child,)
            else:
                args = ()
                bridge = None

            self.__process = Process(
                target=self.run, args=args, name=self.name
            )
            self.__process.daemon = True
            self.__process.start()

            return self.__process, bridge
        else:
            self.__thread = Thread(target=self.run, name=self.name)
            self.__thread.daemon = True
            self.__thread.start()

            return self.__thread, None

    def join(self):
        if self.__thread is not None:
            return self.__thread.join()

        if self.__process is not None:
            return self.__process.join()

    def stop(self, code=None):
        """
        Stop this manager. Invoking this method causes
        an invocation of ``run()`` to return.
        """

        if self.__process not in (None, current_process()) and self.__process.is_alive():
            self.__process.terminate()
            self.__process.join(TIMEOUT)

            if self.__process.is_alive():
                kill(self.__process.pid, SIGKILL)

        if not self.running:
            return

        self._running = False

        self.fire(stopped(self))

        if self.root._executing_thread is None:
            for _ in range(3):
                self.tick()

        if code is not None:
            raise SystemExit(code)

    def processTask(self, event, task, parent=None):  # noqa
        # XXX: C901: This has a high McCabe complexity score of 16.
        # TODO: Refactor this method.

        value = None
        try:
            value = next(task)
            if isinstance(value, CallValue):
                # Done here, next() will StopIteration anyway
                self.unregisterTask((event, task, parent))
                # We are in a callEvent
                value = parent.send(value.value)
                if isinstance(value, GeneratorType):
                    # We loose a yield but we gain one,
                    # we don't need to change
                    # event.waitingHandlers
                    # The below code is delegated to handlers
                    # in the waitEvent generator
                    # self.registerTask((event, value, parent))
                    task_state = next(value)
                    task_state.task_event = event
                    task_state.task = value
                    task_state.parent = parent
                else:
                    event.waitingHandlers -= 1
                    if value is not None:
                        event.value.value = value
                    self.registerTask((event, parent, None))
            elif isinstance(value, GeneratorType):
                event.waitingHandlers += 1
                self.unregisterTask((event, task, None))
                # First yielded value is always the task state
                task_state = next(value)
                task_state.task_event = event
                task_state.task = value
                task_state.parent = task
                # The below code is delegated to handlers
                # in the waitEvent generator
                # self.registerTask((event, value, task))
                # XXX: ^^^ Why is this commented out anyway?
            elif isinstance(value, ExceptionWrapper):
                self.unregisterTask((event, task, parent))
                if parent:
                    value = parent.throw(value.extract())
                    if value is not None:
                        value_generator = (val for val in (value,))
                        self.registerTask((event, value_generator, parent))
                else:
                    raise value.extract()
            elif isinstance(value, Sleep):
                if value is not task:
                    value.task = (event, task, parent)
                    self.registerTask((event, value, parent))
                    self.unregisterTask((event, task, parent))
            elif value is not None:
                event.value.value = value
        except StopIteration:
            event.waitingHandlers -= 1
            self.unregisterTask((event, task, parent))

            if parent:
                self.registerTask((event, parent, None))
            elif hasattr(task, "task"):
                # XXX: The subtask is considered a "waiting handler"
                event.waitingHandlers += 1
                self.registerTask(task.task)
            elif event.waitingHandlers == 0:
                event.value.inform(True)
                self._eventDone(event)
        except KeyboardInterrupt:
            self.stop()
        except SystemExit as e:
            self.stop(e.code)
        except BaseException:
            self.unregisterTask((event, task, parent))

            err = _exc_info()

            event.value.value = err
            event.value.errors = True
            event.value.inform(True)

            if event.failure:
                self.fire(event.child("failure", event, err), *event.channels)

            self.fire(exception(*err, handler=None, fevent=event))

    def tick(self, timeout=-1):
        """
        Execute all possible actions once. Process all registered tasks
        and flush the event queue. If the application is running fire a
        GenerateEvents to get new events from sources.

        This method is usually invoked from :meth:`~.run`. It may also be
        used to build an application specific main loop.

        :param timeout: the maximum waiting time spent in this method. If
            negative, the method may block until at least one action
            has been taken.
        :type timeout: float, measuring seconds
        """
        # process tasks
        if self._tasks:
            for task in self._tasks.copy():
                self.processTask(*task)

        if self._running:
            self.fire(generate_events(self._lock, timeout), "*")

        if len(self._queue):
            self.flush()

    def run(self, socket=None):
        """
        Run this manager. The method fires the
        :class:`~.events.Started` event and then continuously
        calls :meth:`~.tick`.

        The method returns when the manager's
        :meth:`~.stop` method is invoked.

        If invoked by a programs main thread, a signal handler for
        the ``INT`` and ``TERM`` signals is installed. This handler
        fires the corresponding :class:`~.events.Signal`
        events and then calls :meth:`~.stop` for the manager.
        """

        atexit.register(self.stop)

        if current_thread().getName() == "MainThread":
            try:
                set_signal_handler(SIGINT, self._signal_handler)
                set_signal_handler(SIGTERM, self._signal_handler)
            except ValueError:
                # Ignore if we can't install signal handlers
                pass

        self._running = True
        self.root._executing_thread = current_thread()

        # Setup Communications Bridge

        if socket is not None:
            from circuits.core.bridge import Bridge
            Bridge(socket, channel=socket.channel).register(self)

        self.fire(started(self))

        try:
            while self.running or len(self._queue):
                self.tick()
            # Fading out, handle remaining work from stop event
            for _ in range(3):
                self.tick()
        except Exception as exc:
            stderr.write("Unhandled ERROR: {0:s}\n".format(exc))
            stderr.write(format_exc())
        finally:
            try:
                self.tick()
            except Exception:
                pass

        self.root._executing_thread = None
        self.__thread = None
        self.__process = None
