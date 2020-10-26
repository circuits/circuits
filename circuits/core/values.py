"""
This defines the Value object used by components and events.
"""
from ..six import PY2, python_2_unicode_compatible, string_types, text_type
from .events import Event


@python_2_unicode_compatible
class Value(object):

    """Create a new future Value Object

    Creates a new future Value Object which is used by Event Objects and the
    Manager to store the result(s) of an Event Handler's exeuction of some
    Event in the system.

    :param event: The Event this Value is associated with.
    :type  event: Event instance

    :param manager: The Manager/Component used to trigger notifications.
    :type  manager: A Manager/Component instance.

    :ivar result: True if this value has been changed.
    :ivar errors: True if while setting this value an exception occured.
    :ivar notify: True or an event name  to notify of changes to this value

    This is a Future/Promise implementation.
    """

    def __init__(self, event=None, manager=None):
        self.event = event
        self.manager = manager

        self.notify = False
        self.promise = False

        self.result = False
        self.errors = False
        self.parent = self
        self.handled = False

        self._value = None

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["manager"]
        return odict

    def __contains__(self, y):
        value = self.value
        return y in value if isinstance(value, list) else y == value

    def __getitem__(self, y):
        v = self.value[y]
        if isinstance(v, Value):
            return v.value
        else:
            return v

    def __iter__(self):
        return iter(map(lambda v: v.value if isinstance(v, Value) else v,
                        self.value))

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        value = ""
        if self.result:
            value = repr(self.value)

        format = "<Value (%s) result=%r; errors=%r; for %r>"
        return format % (value, self.result, self.errors, self.event)

    def __str__(self):
        "x.__str__() <==> str(x)"
        if PY2:
            return text_type(self.value).encode('utf-8')
        return str(self.value)

    def inform(self, force=False):
        if self.promise and not force:
            return

        notify = getattr(self.event, "notify", False) or self.notify

        if self.manager is not None and notify:
            if isinstance(notify, string_types):
                e = Event.create(notify, self)
            else:
                e = self.event.child("value_changed", self)

            self.manager.fire(e, self.manager)

    def getValue(self, recursive=True):
        value = self._value

        if not recursive:
            return value

        while isinstance(value, Value):
            value = value._value

        return value

    def setValue(self, value):
        if isinstance(value, Value):
            value.parent = self

        if self.result and isinstance(self._value, list):
            self._value.append(value)
        elif self.result:
            self._value = [self._value]
            self._value.append(value)
        else:
            self._value = value

        def update(o, v):
            if isinstance(v, Value):
                o.errors = v.errors
                o.result = v.result
            elif v is not None:
                o.result = True

                o.inform()

            if o.parent is not o:
                o.parent.errors = o.errors
                o.parent.result = o.result
                update(o.parent, v)

        update(self, value)

    value = property(getValue, setValue, None, "Value of this Value")
