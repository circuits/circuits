# Package:  components
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Components

This module defines the BaseComponent and the subclass Component
"""

from itertools import chain
from types import MethodType
from inspect import getmembers
from collections import Callable

from .utils import findroot
from .manager import Manager
from .handlers import HandlerMetaClass, handler
from .events import Registered, Unregistered

class BaseComponent(Manager):
    """Base Component

    This is the Base of the Component which manages registrations to other
    components or managers. Every Base Component and thus Component has a
    unique Channel that is used as a separation of concern for its registered
    Event Handlers. By default, this Channels is None (or also known as the
    Global Channel).

    :ivar channel: The Component's Channel
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
        self._register_handlers()
        self.manager = self

        for k, v in getmembers(self):
            if isinstance(v, BaseComponent):
                v.register(self)

    def _register_handlers(self):
        p = lambda x: isinstance(x, Callable) and getattr(x, "handler", False)
        handlers = [v for k, v in getmembers(self, p)]
        for handler in handlers:
            self.handlers.add(handler)

    def _unregister_handlers(self):
        self.handlers.clear()

    def register(self, manager):
        """Register all Event Handlers with the given Manager
        
        This will register all Event Handlers of this Component to the
        given Manager. By default, every Component (Base Component) is
        registered with itself.
        
        If the Component or Manager being registered
        with is not the current Component, then any Hidden Components
        in registered to this Component will also be registered with the
        given Manager. A Registered Event will also be sent.
        """

        def _register(c, m, r):
            c.root = r
            if c._queue:
                m._queue.extend(list(c._queue))
                c._queue.clear()
            if m is not r:
                if m._queue:
                    r._queue.extend(list(m._queue))
                    m._queue.clear()
            if hasattr(c, "__tick__"):
                m._ticks.add(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.add(getattr(c, "__tick__"))
            [_register(x, m, r) for x in c.components]

        _register(self, manager, findroot(manager))

        self.manager = manager

        if manager is not self:
            manager.components.add(self)
            self.fire(Registered(self, manager), target=self)

        return self

    @handler('unregister')
    def on_unregister(self, component=None):
        if component == self or component == None:
            self.unregister()

    def unregister(self):
        """Unregister all registered Event Handlers
        
        This will unregister all registered Event Handlers of this Component
        from its registered Component or Manager.

        @note: It's possible to unregister a Component from itself!
        """

        def _unregister(c, m, r):
            c.root = self
            if hasattr(c, "__tick__"):
                m._ticks.remove(getattr(c, "__tick__"))
                if m is not r:
                    r._ticks.remove(getattr(c, "__tick__"))

            for x in c.components:
                _unregister(x, m, r)

        self.fire(Unregistered(self, self.manager), target=self)

        root = findroot(self.manager)
        _unregister(self, self.manager, root)

        self.manager.components.discard(self)
        if not root == self:
            self.fire(Unregistered(self, self.manager), target=self)

        self.manager = self

        return self

Component = HandlerMetaClass("Component", (BaseComponent,), {})
