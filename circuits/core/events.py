# Package:  events
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module define the basic Event object and common events.
"""


from .utils import uncamel


class EventMetaClass(type):

    def __init__(cls, name, bases, ns):
        super(EventMetaClass, cls).__init__(name, bases, ns)

        setattr(cls, "name", ns.get("name", uncamel(cls.__name__)))


class BaseEvent(object):

    channels = ()

    success = None
    failure = None
    end = None

    @classmethod
    def create(cls, name, *args, **kwargs):
        return type(cls)(name, (cls,), {})(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        self.args = list(args)
        self.kwargs = kwargs

        self.value = None
        self.future = False
        self.handler = None
        self.notify = False

    def __eq__(self, other):
        return (self.name == other.name
                and self.channels == other.channels
                and self.args == other.args
                and self.kwargs == other.kwargs)

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
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(type, value, traceback, handler)


class End(Event):
    """End Event

    This Event is sent just after all handlers for an event have been run
    """


class Success(Event):
    """Success Event

    This Event is sent when all handlers (for a particular event) have been
    executed successfully.
    """


class Failure(Event):
    """Failure Event

    This Event is sent when an error has occurred with the execution of an
    Event Handlers.

    :param event: The event that failed
    :type  event: Event
    """


class Started(Event):
    """Started Event

    This Event is sent when a Component has started running.

    :param component: The component that was started
    :type  component: Component or Manager
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Started, self).__init__(component)


class Stopped(Event):
    """Stopped Event

    This Event is sent when a Component has stopped running.

    :param component: The component that has stopped
    :type  component: Component or Manager
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

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
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

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
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Registered, self).__init__(component, manager)


class Unregister(Event):
    """Unregister Event

    This Event ask for a Component to unregister from its
    Component or Manager.
    """

    def __init__(self, component=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregister, self).__init__(component)


class Unregistered(Event):
    """Unregistered Event

    This Event is sent when a Component has been unregistered from its
    Component or Manager.
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregistered, self).__init__(component, manager)
