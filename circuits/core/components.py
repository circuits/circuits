# Package:  components
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Components

This module definse the BaseComponent and the subclassed Component
"""

from itertools import chain
from types import MethodType
from inspect import getmembers

from utils import findroot
from manager import Manager
from handlers import HandlersType
from events import Registered, Unregistered

class BaseComponent(Manager):
    """Base Component

    This is the Base of the Component which manages registrations to other
    components or managers. Every Base Component and thus Component has a
    unique Channel that is used as a separation of concern for it's registered
    Event Handlers. By default, this Channels is None (or also known as the
    Global Channel).

    When a Component (Base Component) has a set Channel that is not the Global
    Channel (None), then any Event Handlers will actually listen on a Channel
    that is a combination of the Component's Channel prefixed with the Event
    Handler's Channel. The form becomes:

    C{target:channel}

    Where:
       - target is the Component's Channel
       - channel is the Event Handler's Channel

    :ivar channel: The Component's Channel
    """

    channel = "*"

    def __new__(cls, *args, **kwargs):
        """TODO Work around for Python bug.

        Bug: http://bugs.python.org/issue5322
        """

        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        "initializes x; see x.__class__.__doc__ for signature"

        super(BaseComponent, self).__init__(*args, **kwargs)

        self.channel = kwargs.get("channel", self.channel) or "*"
        self._registerHandlers()
        self.manager = self

        for k, v in getmembers(self):
            if isinstance(v, BaseComponent):
                v.register(self)

    def _registerHandlers(self, manager=None):
        if manager is None:
            p = lambda x: callable(x) and getattr(x, "handler", False)
            handlers = [v for k, v in getmembers(self, p)]
            for handler in handlers:
                target = handler.target or getattr(self, "channel", "*")
                self.add(handler, target=target)
        else:
            for handler in chain(self._globals, self._handlers):
                kwargs = {}
                kwargs = self._handlerattrs[handler]
                if not kwargs.get("target"):
                    kwargs["target"] = getattr(self, "channel", "*")
                if "channels" in kwargs:
                    channels = kwargs["channels"]
                    del kwargs["channels"]
                else:
                    channels = ()
                manager.add(handler, *channels, **kwargs)

    def _unregisterHandlers(self, manager):
        for handler in self._handlers.copy():
            manager.remove(handler)

    def register(self, manager):
        """Register all Event Handlers with the given Manager
        
        This will register all Event Handlers of this Component to the
        given Manager. By default, every Component (Base Component) is
        registered with itself.
        
        Iif the Component or Manager being registered
        with is not the current Component, then any Hidden Components
        in registered to this Component will also be regsitered with the
        given Manager. A Registered Event will also be sent.
        """

        def _register(c, m, r):
            c._registerHandlers(m)
            c.root = r
            if c._queue:
                m._queue.extend(list(c._queue))
                c._queue.clear()
            if m is not r:
                c._registerHandlers(r)
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

    def unregister(self):
        """Unregister all registered Event Handlers
        
        This will unregister all registered Event Handlers of this Component
        from it's registered Component or Manager.

        @note: It's possible to unregister a Component from itself!
        """

        def _unregister(c, m, r):
            c._unregisterHandlers(m)
            c.root = self
            if m is not r:
                c._unregisterHandlers(r)
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

class Component(BaseComponent):

    __metaclass__ = HandlersType

    def __new__(cls, *args, **kwargs):
        self = BaseComponent.__new__(cls, *args, **kwargs)
        handlers = [x for x in cls.__dict__.values() \
                if getattr(x, "handler", False)]
        overridden = lambda x: [h for h in handlers \
                if x.channels == h.channels and getattr(h, "override", False)]
        for base in cls.__bases__:
            if issubclass(cls, base):
                for k, v in base.__dict__.items():
                    p1 = callable(v)
                    p2 = getattr(v, "handler", False)
                    predicate = p1 and p2 and not overridden(v)
                    if predicate:
                        name = "%s_%s" % (base.__name__, k)
                        method = MethodType(v, self)
                        setattr(self, name, method)
        return self
