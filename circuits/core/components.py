"""
This module defines the BaseComponent and its subclass Component.
"""
from inspect import getmembers
from itertools import chain
from types import MethodType
try:
    from collections import Callable
except ImportError:
    from collections.abc import Callable

from .events import Event, registered, unregistered
from .handlers import HandlerMetaClass, handler
from .manager import Manager


class prepare_unregister(Event):

    """
    This event is fired when a component is about to be unregistered
    from the component tree. Unregistering a component actually
    detaches the complete subtree that the unregistered component
    is the root of. Components that need to know if they
    are removed from the main tree (e.g. because they maintain
    relationships to other components in the tree) handle this
    event, check if the component being unregistered is one
    of their ancestors and act accordingly.

    :param component: the component that will be unregistered
    :type  type: :class:`~.BaseComponent`
    """

    complete = True

    def __init__(self, *args, **kwargs):
        super(prepare_unregister, self).__init__(*args, **kwargs)

    def in_subtree(self, component):
        """
        Convenience method that checks if the given *component*
        is in the subtree that is about to be detached.
        """
        while True:
            if component == self.args[0]:
                return True
            if component == component.root:
                return False
            component = component.parent


class BaseComponent(Manager):

    """
    This is the base class for all components in a circuits based application.
    Components can (and should, except for root components) be registered
    with a parent component.

    BaseComponents can declare methods as event handlers using the
    handler decoration (see :func:`circuits.core.handlers.handler`). The
    handlers are invoked for matching events from the
    component's channel (specified as the component's ``channel`` attribute).

    BaseComponents inherit from :class:`circuits.core.manager.Manager`.
    This provides components with the
    :func:`circuits.core.manager.Manager.fireEvent` method that can
    be used to fire events as the result of some computation.

    Apart from the ``fireEvent()`` method, the Manager nature is important
    for root components that are started or run.

    :ivar channel: a component can be associated with a specific channel
        by setting this attribute. This should either be done by
        specifying a class attribute *channel* in the derived class or by
        passing a keyword parameter *channel="..."* to *__init__*.
        If specified, the component's handlers receive events on the
        specified channel only, and events fired by the component will
        be sent on the specified channel (this behavior may be overridden,
        see :class:`~circuits.core.events.Event`, :meth:`~.fireEvent` and
        :func:`~circuits.core.handlers.handler`). By default, the channel
        attribute is set to "*", meaning that events are fired on all
        channels and received from all channels.
    """

    channel = "*"

    def __new__(cls, *args, **kwargs):
        self = super(BaseComponent, cls).__new__(cls)

        handlers = dict(
            [(k, v) for k, v in list(cls.__dict__.items())
                if getattr(v, "handler", False)]
        )

        def overridden(x):
            return x in handlers and handlers[x].override

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
            # TODO: Document this feature. See Issue #88
            if v is not self and isinstance(v, BaseComponent) \
                    and v not in ('parent', 'root'):
                v.register(self)

        if hasattr(self, "init") and isinstance(self.init, Callable):
            self.init(*args, **kwargs)

        @handler("prepare_unregister_complete", channel=self)
        def _on_prepare_unregister_complete(self, event, e, value):
            self._do_prepare_unregister_complete(event.parent, value)
        self.addHandler(_on_prepare_unregister_complete)

    def register(self, parent):
        """
        Inserts this component in the component tree as a child
        of the given *parent* node.

        :param parent: the parent component after registration has completed.
        :type parent: :class:`~.manager.Manager`

        This method fires a :class:`~.events.Registered` event to inform
        other components in the tree about the new member.
        """

        self.parent = parent
        self.root = parent.root

        # Make sure that structure is consistent before firing event
        # because event may be handled in a concurrent thread.
        if parent is not self:
            parent.registerChild(self)
            self._updateRoot(parent.root)
            self.fire(registered(self, self.parent))
        else:
            self._updateRoot(parent.root)

        return self

    def unregister(self):
        """
        Removes this component from the component tree.

        Removing a component from the component tree is a two stage process.
        First, the component is marked as to be removed, which prevents it
        from receiving further events, and a
        :class:`~.components.prepare_unregister` event is fired. This
        allows other components to e.g. release references to the component
        to be removed before it is actually removed from the component tree.

        After the processing of the ``prepare_unregister`` event has completed,
        the component is removed from the tree and an
        :class:`~.events.unregistered` event is fired.
        """

        if self.unregister_pending or self.parent is self:
            return self

        # tick shouldn't be called anymore, although component is still in tree
        self._unregister_pending = True
        self.root._cache_needs_refresh = True

        # Give components a chance to prepare for unregister
        evt = prepare_unregister(self)
        evt.complete_channels = (self,)
        self.fire(evt)

        return self

    @property
    def unregister_pending(self):
        return getattr(self, "_unregister_pending", False)

    def _do_prepare_unregister_complete(self, e, value):
        # Remove component from tree now
        delattr(self, "_unregister_pending")
        self.fire(unregistered(self, self.parent))

        if self.parent is not self:
            self.parent.unregisterChild(self)
            self.parent = self

        self._updateRoot(self)
        return self

    def _updateRoot(self, root):
        self.root = root
        for c in self.components:
            c._updateRoot(root)

    @classmethod
    def handlers(cls):
        """Returns a list of all event handlers for this Component"""

        return list(set(
            getattr(cls, k) for k in dir(cls)
            if getattr(getattr(cls, k), "handler", False)
        ))

    @classmethod
    def events(cls):
        """Returns a list of all events this Component listens to"""

        handlers = (
            getattr(cls, k).names for k in dir(cls)
            if getattr(getattr(cls, k), "handler", False)
        )

        return list(set(
            name for name in chain(*handlers)
            if not name.startswith("_")
        ))

    @classmethod
    def handles(cls, *names):
        """Returns True if all names are event handlers of this Component"""

        return all(name in cls.events() for name in names)


Component = HandlerMetaClass("Component", (BaseComponent,), {})
"""
If you use Component instead of BaseComponent as base class for your own
component class, then all methods that are not marked as private
(i.e: start with an underscore) are automatically decorated as handlers.

The methods are invoked for all events from the component's channel
where the event's name matches the method's name.
"""
