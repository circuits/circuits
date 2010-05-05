# Package:  values
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Values

This defines the Value object used by components and events.
"""

from types import ListType
from itertools import imap

from events import Event

class ValueChanged(Event):
    """Value Changed Event

    This Event is triggered when the return Value of an Event Handler has
    changed it's value.
    """

    def __init__(self, value):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(ValueChanged, self).__init__(value)


class Value(object):
    """Create a new future Value Object

    Creates a new future Value Object which is used by Event Objects and the
    Manager to store the result(s) of an Event Handler's exeuction of some
    Event in the system.

    :param event: The Event this Value is associated with.
    :type  event: Event instance

    :param manager: The Manager/Component used to trigger notifications.
    :type  manager: A Manager/Component instance.

    :param onSet: The channel used when triggering ValueChagned events.
    :type  onSet: A (channel, target) tuple.

    :ivar result: True if this value has been changed.
    :ivar errors: True if while setting this value an exception occured.

    This is a Future/Promise implementation.
    """

    def __init__(self, event=None, manager=None, onSet=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        self.event = event
        self.manager = manager

        self.onSet = onSet

        self.result = False
        self.errors = False
        self._parent = self
        self._value = None

    def __eq__(self, other):
        return (self.__class__ is other.__class__
                and self.event == other.event
                and self.result == other.result
                and self.errors == other.errors
                and self._value == other._value)

    def __getstate__(self):
        keys = ("event", "onSet", "result", "errors", "_value")
        return dict([(k, getattr(self, k, None)) for k in keys])

    def __contains__(self, y):
        value = self.value
        return y in value if type(value) is ListType else y == value

    def __getitem__(self, y):
        v = self.value[y]
        if isinstance(v, Value):
            return v.value
        else:
            return v

    def __iter__(self):
        return imap(lambda v: v.value if isinstance(v, Value) else v,
                self.value)

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        value = ""
        if self.result:
            value = repr(self.value)

        format = "<Value (%s) result: %r errors: %r for %r"
        return format % (value, self.result, self.errors, self.event)

    def __str__(self):
        "x.__str__() <==> str(x)"

        return str(self.value)

    def getValue(self):
        value = self._value
        while isinstance(value, Value):
            value = value._value
        return value

    def setValue(self, value):
        if isinstance(value, Value):
            value._parent = self

        if self.result and type(self._value) is ListType:
            self._value.append(value)
        elif self.result:
            self._value = [self._value]
            self._value.append(value)
        else:
            self._value = value

        def notify(o, v):
            if not isinstance(v, Value) and v is not None:
                o.result = True
                if o.manager is not None and o.onSet is not None:
                    o.manager.fireEvent(ValueChanged(o), *o.onSet)
            elif isinstance(v, Value):
                o.errors = v.errors
                o.result = v.result
            if not o._parent == o:
                notify(o._parent, v)
        
        notify(self, value)

    value = property(getValue, setValue, None, "Value of this Value")
