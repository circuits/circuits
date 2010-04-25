# Package:  events
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module define the basic Event object and commmon events.
"""

class Event(object):
    """Create a new Event Object

    Create a new Event Object populating it with the given list of arguments
    and keyword arguments.

    :ivar name:    The name of the Event
    :ivar channel: The channel this Event is bound for
    :ivar target:  The target Component this Event is bound for
    :ivar success: An optional channel to use for Event Handler success
    :ivar failure: An optional channel to use for Event Handler failure
    :ivar filter: An optional channel to use if an Event is filtered
    :ivar start: An optional channel to use before an Event starts
    :ivar end: An optional channel to use when an Event ends

    :ivar value: The future Value object used to store the result of an event

    :param args: list of arguments
    :type  args: tuple

    :param kwargs: dct of keyword arguments
    :type  kwargs: dict
    """

    channel = None
    target = None

    handler = None
    success = None
    failure = None
    filter = None
    start = None
    end = None

    value = None

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        self.args = list(args)
        self.kwargs = kwargs

    def __getstate__(self):
        keys = ("args", "kwargs", "channel", "target", "success", "failure",
                "filter", "start", "end", "value", "source")
        return dict([(k, getattr(self, k, None)) for k in keys])

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

    channel = "exception"

    def __init__(self, type, value, traceback, handler=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(type, value, traceback, handler)


class Success(Event):
    """Success Event

    This Event is sent when an Event Handler's execution has completed
    successfully.

    :param evt: The event that succeeded
    :type  evt: Event

    :param handler: The handler that executed this event
    :type  handler: @handler

    :param retval: The returned value of the handler
    :type  retval: object
    """

    def __init__(self, event, handler, retval):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Success, self).__init__(event, handler, retval)


class Failure(Event):
    """Failure Event

    This Event is sent when an error has occured with the execution of an
    Event Handlers.

    :param evt: The event that failued
    :type  evt: Event

    :param handler: The handler that failed
    :type  handler: @handler

    :param error: A tuple containing the exception that occured
    :type  error: (etype, evalue, traceback)
    """

    def __init__(self, event, handler, error):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Failure, self).__init__(event, handler, error)


class Filter(Event):
    """Filter Event

    This Event is sent when an Event is filtered by some Event Handler.

    :param evt: The event that was filtered
    :type  evt: Event

    :param handler: The handler that filtered this event
    :type  handler: @handler

    :param retval: The returned value of the handler
    :type  retval: object
    """

    def __init__(self, event, handler, retval):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Filter, self).__init__(event, handler, retval)


class Start(Event):
    """Start Event

    This Event is sent just before an Event is started

    :param evt: The event about to start
    :type  evt: Event
    """

    def __init__(self, event):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Start, self).__init__(event)


class End(Event):
    """End Event

    This Event is sent just after an Event has ended

    :param evt: The event that has finished
    :type  evt: Event

    :param handler: The last handler that executed this event
    :type  handler: @handler

    :param retval: The returned value of the last handler
    :type  retval: object
    """

    def __init__(self, event, handler, retval):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(End, self).__init__(event, handler, retval)


class Started(Event):
    """Started Event

    This Event is sent when a Component has started running.

    :param component: The component that was started
    :type  component: Component or Manager

    :param mode: The mode in which the Component was started,
                 P (Process), T (Thread) or None (Main Thread / Main Process).
    :type  str:  str or None
    """

    def __init__(self, component, mode):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Started, self).__init__(component, mode)


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

class Unregistered(Event):
    """Unregistered Event

    This Event is sent when a Component has been unregistered from it's
    Component or Manager.
    """

    def __init__(self, component, manager):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Unregistered, self).__init__(component, manager)
