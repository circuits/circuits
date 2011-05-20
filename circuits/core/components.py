# Package:  components
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Components

This module defines the BaseComponent and the subclass Component
"""

from itertools import chain
from types import MethodType
from inspect import getmembers

from .utils import findroot
from .manager import Manager
from .handlers import HandlerMetaClass, handler
from .events import Registered, Unregistered
import collections

class BaseComponent(Manager):
    """Base Component

    ...
    """

    channel = "*"

    def __new__(cls, *args, **kwargs):
        self = super(BaseComponent, cls).__new__(cls)

        handlers = dict([(k, v) for k, v in cls.__dict__.items()
                if getattr(v, "handler", False)])

        overridden = lambda x: x in handlers and handlers[x].override

        for base in cls.__bases__:
            if issubclass(cls, base):
                for k, v in list(base.__dict__.items()):
                    p1 = isinstance(v, collections.Callable)
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
                if not v.names and v.channel == "*":
                    self._globals.add(v)
                for name in v.names:
                    self._handlers.setdefault(name, set()).add(v)
            if isinstance(v, BaseComponent):
                v.register(self)

    def register(self, parent):
        """Register all Event Handlers with the given Manager
        
        This will register all Event Handlers of this Component to the
        given Manager. By default, every Component (Base Component) is
        registered with itself.
        
        If the Component or Manager being registered
        with is not the current Component, then any Hidden Components
        in registered to this Component will also be registered with the
        given Manager. A Registered Event will also be sent.
        """
        if parent != self:
            parent.registerChild(self)

        # what's the difference between manager and root ?
        self.parent = parent
        self.root = parent.root

        self.fire(Registered(self, self.parent))
        return self

    def unregister(self):
        """Unregister all registered Event Handlers
        
        This will unregister all registered Event Handlers of this Component
        from its registered Component or Manager.

        @note: It's possible to unregister a Component from itself!
        """
        self.fire(Unregistered(self, self.parent))

        self.parent.unregisterChild(self)

        self.parent = self.root = self

        return self

Component = HandlerMetaClass("Component", (BaseComponent,), {})

