"""
This module defines the basic event class and common events.
"""
from inspect import ismethod
from traceback import format_tb


class Event(object):

    channels = ()
    "The channels this message is sent to."

    parent = None
    notify = False
    success = False
    failure = False
    complete = False
    alert_done = False
    waitingHandlers = 0

    @classmethod
    def create(cls, _name, *args, **kwargs):
        return type(cls)(_name, (cls,), {})(*args, **kwargs)

    def child(self, name, *args, **kwargs):
        e = Event.create(
            "{0:s}_{1:s}".format(self.name, name), *args, **kwargs
        )
        e.parent = self
        return e

    def __init__(self, *args, **kwargs):
        """An event is a message send to one or more channels.
        It is eventually dispatched to all components
        that have handlers for one of the channels and the event type.

        All normal arguments and keyword arguments passed to the constructor
        of an event are passed on to the handler. When declaring a
        handler, its argument list must therefore match the arguments
        used for creating the event.

        Every event has a :attr:`name` attribute that is used for matching
        the event with the handlers.

        :cvar channels: an optional attribute that may be set before firing
            the event. If defined (usually as a class variable), the attribute
            specifies the channels that the event should be delivered
            to as a tuple. This overrides the default behavior
            of sending the event to the firing component's channel.

            When an event is fired, the value in this attribute
            is replaced for the instance with the channels that
            the event is actually sent to. This information may be used
            e.g. when the event is passed as a parameter to a handler.

        :ivar value: this is a :class:`circuits.core.values.Value`
            object that holds the results returned by the handlers invoked
            for the event.

        :var success: if this optional attribute is set to
            ``True``, an associated event ``success`` (original name
            with "_success" appended) will automatically be fired when all
            handlers for the event have been invoked successfully.

        :var success_channels: the success event is, by default, delivered
            to same channels as the successfully dispatched event itself.
            This may be overridden by specifying an alternative list of
            destinations using this attribute.

        :var complete: if this optional attribute is set to
            ``True``, an associated event ``complete`` (original name
            with "_complete" appended) will automatically be fired when all
            handlers for the event and all events fired by these handlers
            (recursively) have been invoked successfully.

        :var complete_channels: the complete event is, by default, delivered
            to same channels as the initially dispatched event itself.
            This may be overridden by specifying an alternative list of
            destinations using this attribute.
        """

        self.args = list(args)
        self.kwargs = kwargs

        self.uid = None
        self.value = None
        self.handler = None
        self.stopped = False
        self.cancelled = False
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["handler"]
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        if len(self.channels) > 1:
            channels = repr(self.channels)
        elif len(self.channels) == 1:
            channels = str(self.channels[0])
        else:
            channels = ""

        data = "%s %s" % (
            ", ".join(repr(arg) for arg in self.args),
            ", ".join("%s=%s" % (k, repr(v)) for k, v in self.kwargs.items())
        )

        return "<%s[%s] (%s)>" % (self.name, channels, data)

    def __getitem__(self, x):
        """x.__getitem__(y) <==> x[y]

        Get and return data from the event object requested by "x".
        If an int is passed to x, the requested argument from self.args
        is returned index by x. If a str is passed to x, the requested
        keyword argument from self.kwargs is returned keyed by x.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if isinstance(x, int):
            return self.args[x]
        elif isinstance(x, str):
            return self.kwargs[x]
        else:
            raise TypeError("Expected int or str, got %r" % type(x))

    def __setitem__(self, i, y):
        """x.__setitem__(i, y) <==> x[i] = y

        Modify the data in the event object requested by "x".
        If i is an int, the ith requested argument from self.args
        shall be changed to y. If i is a str, the requested value
        keyed by i from self.kwargs, shall by changed to y.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if isinstance(i, int):
            self.args[i] = y
        elif isinstance(i, str):
            self.kwargs[i] = y
        else:
            raise TypeError("Expected int or str, got %r" % type(i))

    def cancel(self):
        """Cancel the event from being processed (if not already)"""

        self.cancelled = True

    def stop(self):
        """Stop further processing of this event"""

        self.stopped = True


class exception(Event):

    """exception Event

    This event is sent for any exceptions that occur during the execution
    of an event Handler that is not SystemExit or KeyboardInterrupt.

    :param type: type of exception
    :type  type: type

    :param value: exception object
    :type  value: exceptions.Exceptions

    :param traceback: traceback of exception
    :type  traceback: traceback

    :param handler: handler that raised the exception
    :type  handler: @handler(<method>)

    :param fevent: event that failed
    :type  fevent: event
    """

    def __init__(self, type, value, traceback, handler=None, fevent=None):
        super(exception, self).__init__(type, value,
                                        self.format_traceback(traceback),
                                        handler=handler, fevent=fevent)

    def format_traceback(self, traceback):
        return format_tb(traceback)


class started(Event):

    """started Event

    This Event is sent when a Component or Manager has started running.

    :param manager: The component or manager that was started
    :type  manager: Component or Manager
    """

    def __init__(self, manager):
        super(started, self).__init__(manager)


class stopped(Event):

    """stopped Event

    This Event is sent when a Component or Manager has stopped running.

    :param manager: The component or manager that has stopped
    :type  manager: Component or Manager
    """

    def __init__(self, manager):
        super(stopped, self).__init__(manager)


class signal(Event):

    """signal Event

    This Event is sent when a Component receives a signal.

    :param signo: The signal number received.
    :type  int:   An int value for the signal

    :param stack:  The interrupted stack frame.
    :type  object: A stack frame
    """

    def __init__(self, signo, stack):
        super(signal, self).__init__(signo, stack)


class registered(Event):

    """registered Event

    This Event is sent when a Component has registered with another Component
    or Manager. This Event is only sent if the Component or Manager being
    registered which is not itself.

    :param component: The Component being registered
    :type  component: Component

    :param manager: The Component or Manager being registered with
    :type  manager: Component or Manager
    """

    def __init__(self, component, manager):
        super(registered, self).__init__(component, manager)


class unregistered(Event):

    """unregistered Event

    This Event is sent when a Component has been unregistered from its
    Component or Manager.
    """


class generate_events(Event):

    """generate_events Event

    This Event is sent by the circuits core. All components that generate
    timed events or events from external sources (e.g. data becoming
    available) should fire any pending events in their "generate_events"
    handler.

    The handler must either call :meth:`~stop` (*preventing other handlers
    from being called in the same iteration)
    or must invoke :meth:`~.reduce_time_left` with parameter 0.

    :param max_wait: maximum time available for generating events.
    :type  time_left: float

    Components that actually consume time waiting for events to be generated,
    thus suspending normal execution, must provide a method ``resume``
    that interrupts waiting for events.
    """

    def __init__(self, lock, max_wait):
        super(generate_events, self).__init__()

        self._time_left = max_wait
        self._lock = lock

    @property
    def time_left(self):
        """
        The time left for generating events. A value less than 0
        indicates unlimited time. You should have only
        one component in your system (usually a poller component) that
        spends up to "time left" until it generates an event.
        """

        return self._time_left

    def reduce_time_left(self, time_left):
        """
        Update the time left for generating events. This is typically
        used by event generators that currently don't want to generate
        an event but know that they will within a certain time. By
        reducing the time left, they make sure that they are reinvoked
        when the time for generating the event has come (at the latest).

        This method can only be used to reduce the time left. If the
        parameter is larger than the current value of time left, it is
        ignored.

        If the time left is reduced to 0 and the event is currently
        being handled, the handler's *resume* method is invoked.
        """

        with self._lock:
            if time_left >= 0 and (self._time_left < 0 or self._time_left > time_left):
                self._time_left = time_left
                if self._time_left == 0 and self.handler is not None:
                    m = getattr(
                        getattr(
                            self.handler, "im_self", getattr(
                                self.handler, "__self__"
                            )
                        ),
                        "resume", None
                    )
                    if m is not None and ismethod(m):
                        m()

    @property
    def lock(self):
        return self._lock
