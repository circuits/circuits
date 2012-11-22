# Package:  events
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
This module defines the basic Event class and common events.
"""

from .utils import uncamel
from inspect import ismethod


class EventMetaClass(type):

    def __init__(cls, name, bases, ns):
        super(EventMetaClass, cls).__init__(name, bases, ns)

        setattr(cls, "name", ns.get("name", uncamel(cls.__name__)))


class BaseEvent(object):

    channels = ()
    "The channels this message is send to."

    success = False
    failure = False
    complete = False
    alert_done = False
    waitingHandlers = 0

    @classmethod
    def create(cls, name, *args, **kwargs):
        return type(cls)(name, (cls,), {})(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """An Event is a message send to one or more channels. It is eventually
        dispatched to all components that have handlers for one
        of the channels and the event type.

        All normal arguments and keyword arguments passed to the constructor
        of an event are passed on to the handler. When declaring a
        handler, its argument list must therefore match the arguments
        used for creating the event.

        Every event has a :attr:`name` attribute that is used for matching
        the event with the handlers. By default, the name is the uncameled
        class name of the event.

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
            ``True``, an associated event ``EventSuccess`` (original name
            with "Success" appended) will automatically be fired when all
            handlers for the event have been invoked successfully.

        :var success_channels: the success event is, by default, delivered 
            to same channels as the successfully dispatched event itself. 
            This may be overridden by specifying an alternative list of 
            destinations using this attribute.
        
        :var complete: if this optional attribute is set to
            ``True``, an associated event ``EventComplete`` (original name
            with "Complete" appended) will automatically be fired when all
            handlers for the event and all events fired by these handlers
            (recursively) have been invoked successfully.

        :var success_channels: the complete event is, by default, delivered 
            to same channels as the initially dispatched event itself. 
            This may be overridden by specifying an alternative list of 
            destinations using this attribute.
        """

        self.args = list(args)
        self.kwargs = kwargs

        self.value = None
        self.future = False
        self.handler = None
        self.notify = False

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        name = self.name
        type = self.__class__.__name__
        if len(self.channels) > 1:
            channels = repr(self.channels)
        elif len(self.channels) == 1:
            channels = str(self.channels[0])
        else:
            channels = ""

        data = "%s %s" % (
                ", ".join(repr(arg) for arg in self.args),
                ", ".join("%s=%s" % (k, repr(v)) for k, v in
                    self.kwargs.items()
                )
        )

        return "<%s[%s.%s] (%s)>" % (type, channels, name, data)

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

    def __setitem__(self, i, y):
        """x.__setitem__(i, y) <==> x[i] = y

        Modify the data in the Event object requested by "x".
        If i is an int, the ith requested argument from self.args
        shall be changed to y. If i is a str, the requested value
        keyed by i from self.kwargs, shall by changed to y.
        Otherwise a TypeError is raised as nothing else is valid.
        """

        if type(i) is int:
            self.args[i] = y
        elif type(i) is str:
            self.kwargs[i] = y
        else:
            raise TypeError("Expected int or str, got %r" % type(i))

Event = EventMetaClass("Event", (BaseEvent,), {})

class LiteralEvent(Event):
    """
    An event whose name is not uncameled when looking for a handler.
    """
    @staticmethod
    def create(cls, name, *args, **kwargs):
        """
        Utility method to create an event that inherits from
        a base event class (passed in as *cls*) and from
        LiteralEvent.
        """
        return type(cls)(name, (cls, LiteralEvent),
                         {"name": name})(*args, **kwargs)


class DerivedEvent(Event):
    
    @classmethod
    def create(cls, topic, event, *args, **kwargs):
        if isinstance(event, LiteralEvent):
            name = "%s%s" % (event.__class__.__name__, uncamel("_%s" % topic))
            return type(cls)(name, (cls,), 
                             {"name": name})(event, *args, **kwargs)
        else:
            name = "%s_%s" % (event.__class__.__name__, topic)
            return type(cls)(name, (cls,), {})(event, *args, **kwargs)
    

class Error(Event):
    """Error Event

    This Event is sent for any exceptions that occur during the execution
    of an Event Handler that is not SystemExit or KeyboardInterrupt.

    :param type: type of exception
    :type  type: type

    :param value: exception object
    :type  value: exceptions.TypeError

    :param traceback: traceback of exception
    :type  traceback: traceback

    :param kwargs: (Optional) Additional Information
    :type  kwargs: dict
    """

    def __init__(self, type, value, traceback, handler=None):
        super(Error, self).__init__(type, value, traceback, handler)


class Done(DerivedEvent):
    """Done Event

    This Event is sent when an event is done. It is used by the wait and call
    primitives to know when to stop waiting. Don't use this for application
    development, use :class:`Success` instead.
    """
    def __init__(self, *args, **kwargs):
        super(Done, self).__init__(*args, **kwargs)


class Success(DerivedEvent):
    """Success Event

    This Event is sent when all handlers (for a particular event) have been
    executed successfully, see :class:`~.manager.Manager`.

    :param event: The event that has completed.
    :type  event: Event
    """
    def __init__(self, *args, **kwargs):
        super(Success, self).__init__(*args, **kwargs)


class Complete(DerivedEvent):
    """Complete Event

    This Event is sent when all handlers (for a particular event) have been
    executed and (recursively) all handlers for all events fired by those
    handlers etc., see :class:`~.manager.Manager`.

    :param event: The event that has completed.
    :type  event: Event
    """
    def __init__(self, *args, **kwargs):
        super(Complete, self).__init__(*args, **kwargs)


class Failure(DerivedEvent):
    """Failure Event

    This Event is sent when an error has occurred with the execution of an
    Event Handlers.

    :param event: The event that failed
    :type  event: Event
    """
    def __init__(self, *args, **kwargs):
        super(DerivedEvent, self).__init__(*args, **kwargs)    


class Started(Event):
    """Started Event

    This Event is sent when a Component has started running.

    :param component: The component that was started
    :type  component: Component or Manager
    """

    def __init__(self, component):
        super(Started, self).__init__(component)


class Stopped(Event):
    """Stopped Event

    This Event is sent when a Component has stopped running.

    :param component: The component that has stopped
    :type  component: Component or Manager
    """

    def __init__(self, component):
        super(Stopped, self).__init__(component)


class Signal(Event):
    """Signal Event

    This Event is sent when a Component receives a signal.

    :param signal: The signal number received.
    :type  int:    An int value for the signal

    :param stack:  The interrupted stack frame.
    :type  object: A stack frame
    """

    def __init__(self, signal, stack):
        super(Signal, self).__init__(signal, stack)


class Registered(Event):
    """Registered Event

    This Event is sent when a Component has registered with another Component
    or Manager. This Event is only sent iif the Component or Manager being
    registered with is not itself.

    :param component: The Component being registered
    :type  component: Component

    :param manager: The Component or Manager being registered with
    :type  manager: Component or Manager
    """

    def __init__(self, component, manager):
        super(Registered, self).__init__(component, manager)


class Unregister(Event):
    """Unregister Event

    This Event ask for a Component to unregister from its
    Component or Manager.
    """

    def __init__(self, component=None):
        super(Unregister, self).__init__(component)


class Unregistered(Event):
    """Unregistered Event

    This Event is sent when a Component has been unregistered from its
    Component or Manager.
    """

    def __init__(self, component, manager):
        super(Unregistered, self).__init__(component, manager)

class GenerateEvents(Event):
    """Generate events event
    
    This event is sent by the circuits core. All components that generate
    timed events or events from external sources (e.g. data becoming
    available) should fire any pending events in their "generate_events"
    handler.
    
    :param max_wait: maximum time available for generating events. 
    :type  time_left: float
    
    Components that actually consume time waiting for events to be generated,
    thus suspending normal execution, must provide a method ``resume`` 
    that interrupts waiting for events.
    """

    def __init__(self, lock, max_wait):
        super(GenerateEvents, self).__init__()
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
            if time_left >= 0 and (self._time_left < 0 
                                   or self._time_left > time_left):
                self._time_left = time_left
                if self._time_left == 0 and self.handler is not None:
                    m = getattr(self.handler.im_self, "resume", None)
                    if m is not None and ismethod(m):
                        m()

    @property
    def lock(self):
        return self._lock
    