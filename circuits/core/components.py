# Package:  components
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Components

This module defines the BaseComponent and the subclass Component
"""

from types import MethodType
from collections import Callable
from inspect import getmembers, isclass

from .manager import Manager
from .utils import flatten, findroot
from .events import Registered, Unregistered
from .handlers import handler, HandlerMetaClass


def check_singleton(x, y):
    """Return False if x is a singleton and already a member of y"""

    singleton = getattr(x, "singleton", False)

    if isclass(singleton) and issubclass(singleton, Manager):
        return any([isinstance(c, singleton) for c in flatten(findroot(y))])
    elif singleton:
        return any([type(x) in c for c in flatten(findroot(y))])
    else:
        return False


class SingletonError(Exception):
    """Singleton Error

    Raised if a Component with the `singleton` class attribute is True.
    """


class BaseComponent(Manager):
    """Base Component

    ...
    """

    channel = "*"
    singleton = False

    def __new__(cls, *args, **kwargs):
        self = super(BaseComponent, cls).__new__(cls)

        handlers = dict([(k, v) for k, v in cls.__dict__.items()
                if getattr(v, "handler", False)])

        overridden = lambda x: x in handlers and handlers[x].override

        for base in cls.__bases__:
            if issubclass(cls, base):
                for k, v in list(base.__dict__.items()):
                    p1 = isinstance(v, Callable)
                    p2 = getattr(v, "handler", False)
                    p3 = overridden(k)
                    if p1 and p2 and not p3:
                        name = "%s_%s" % (base.__name__, k)
                        method = MethodType(v, self)
                        setattr(self, name, method)

        return self

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(BaseComponent, self).__init__(*args, **kwargs)

        self.channel = kwargs.get("channel", self.channel) or "*"

        for k, v in getmembers(self):
            if getattr(v, "handler", False) is True:
                self.addHandler(v)
            if v is not self and isinstance(v, BaseComponent) \
                    and v not in ('parent', 'root'):
                v.register(self)

    def register(self, parent):
        if check_singleton(self, parent):
            raise SingletonError(self)

        self.parent = parent
        self.root = parent.root

        if parent is not self:
            parent.registerChild(self)
            self.fire(Registered(self, self.parent))

        self._updateRoot(parent.root)

        return self

    @handler('unregister')
    def _on_unregister(self, component):
        if component is not self:
            return
        return self.unregister()

    def unregister(self):
        self.fire(Unregistered(self, self.parent))

        if self.parent is not self:
            self.parent.unregisterChild(self)
            self.parent = self

        self._updateRoot(self)

        return self

    def _updateRoot(self, root):
        self.root = root
        for c in self.components:
            c._updateRoot(root)

Component = HandlerMetaClass("Component", (BaseComponent,), {})
