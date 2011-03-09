# Package:  values
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Values

This defines the Value object used by components and events.
"""


from .events import Event

class ValueChanged(Event):
    """Value Changed Event

    This Event is triggered when the return Value of an Event Handler has
    changed it's value.
    """

    def __init__(self, value):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(ValueChanged, self).__init__(value)

class Proxy(object):

    __slots__ = ["_obj", "_result", "__weakref__"]

    def __init__(self, obj, result=None):
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_result", result)

    #
    # Special Cases
    #

    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    #
    # Special Methods
    #

    _special_methods = [
        "__abs__", "__add__", "__and__", "__call__", "__cmp__",
        "__coerce__", "__contains__", "__delitem__", "__delslice__",
        "__div__", "__divmod__", "__eq__", "__float__", "__floordiv__",
        "__ge__", "__getitem__", "__getslice__", "__gt__", "__hash__",
        "__hex__", "__iadd__", "__iand__", "__idiv__", "__idivmod__",
        "__ifloordiv__", "__ilshift__", "__imod__", "__imul__",
        "__int__", "__invert__", "__ior__", "__ipow__", "__irshift__", 
        "__isub__", "__iter__", "__itruediv__", "__ixor__", "__le__",
        "__len__", "__long__", "__lshift__", "__lt__", "__mod__",
        "__mul__", "__ne__", "__neg__", "__oct__", "__or__", "__pos__",
        "__pow__", "__radd__", "__rand__", "__rdiv__", "__rdivmod__",
        "__reduce__", "__reduce_ex__", "__repr__", "__reversed__",
        "__rfloorfiv__", "__rlshift__", "__rmod__",  "__rmul__",
        "__ror__", "__rpow__", "__rrshift__", "__rshift__", "__rsub__", 
        "__rtruediv__", "__rxor__", "__setitem__", "__setslice__",
        "__sub__", "__truediv__", "__xor__", "next",
    ]
    
    @classmethod
    def _create_class_proxy(cls, theclass):
        """Creates a proxy for the given class"""
        
        def make_method(name):
            def method(self, *fargs, **fkwargs):
                args, kwargs = [], {}
                for i, farg in enumerate(fargs):
                    if isinstance(farg, self.__class__):
                        args.append(object.__getattribute__(farg, "_obj"))
                    else:
                        args.append(farg)

                for k, v in fkwargs.items():
                    if isinstance(v, self.__class__):
                        kwargs[k] = object.__getattribute__(v, "_obj")
                    else:
                        kwargs[k] = v

                result = object.__getattribute__(self, "_result")
                if result is not None:
                    manager()

                return getattr(object.__getattribute__(self, "_obj"),
                        name)(*args, **kwargs)
            return method
        
        namespace = {}
        for method in cls._special_methods:
            if hasattr(theclass, method):
                namespace[method] = make_method(method)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,),
                namespace)
    
    def __new__(cls, obj, manager=None, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class" __init__, so deriving classes can define an 
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """

        theclass = cls._create_class_proxy(obj.__class__)
        self = object.__new__(theclass)
        theclass.__init__(self, obj, *args, **kwargs)
        return self

class Value(object):

    def __init__(self, value=None):
        super(Value, self).__init__()

        if value is not None:
            self._value = Proxy(value)
        else:
            self._value = None

    def __get__(self, instance, owner):
        print("Retriving value...")
        print(instance)
        print(owner)

        return self._value

    def __set__(self, instance, value):
        print("Setting value...")
        print(instance)
        print(value)

        if isinstance(value, instance):
            instance._parent = value

        if value is not None:
            self._value = Proxy(value)

        def notify(o, v):
            if not isinstance(v, Result) and v is not None:
                o.done = True
                if o.manager is not None and o.onSet is not None:
                    o.manager.fireEvent(ValueChanged(o), *o.onSet)
            elif isinstance(v, Result):
                o.done = v.done
                o.errors = v.errors
            if not o._parent == o:
                o._parent.done = o.done
                o._parent.errors = o.errors
                notify(o._parent, v)
        
        notify(self, value)

class Result(object):
    """Create a new Result Object

    Creates a new Result Object which is used by Event Objects and the
    Manager to store the result(s) of an Event Handler's exeuction of some
    Event in the system.

    :param event: The Event this Value is associated with.
    :type  event: Event instance

    :param manager: The Manager/Component used to trigger notifications.
    :type  manager: A Manager/Component instance.

    :param onSet: The channel used when triggering ValueChagned events.
    :type  onSet: A (channel, target) tuple.

    :ivar done:   True if this result has been set.
    :ivar errors: True if while setting this result an exception occured.
    """

    value = Value()

    def __init__(self, event=None, manager=None, onSet=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Result, self).__init__()

        self.event = event
        self.manager = manager

        self.onSet = onSet

        self.done = False
        self.errors = False

        self._parent = None

    def __getstate__(self):
        keys = ("event", "onSet", "done", "errors", "value")
        return dict([(k, getattr(self, k, None)) for k in keys])

    def __repr__(self):
        "x.__repr__() <==> repr(x)"

        format = "<Result (done: %r errors: %r) for %r>"
        return format % (self.done, self.errors, self.event)
