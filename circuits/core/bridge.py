# Module:   bridge
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Bridge

Bridge Component to Bridge one or more components in a single System.
That is, events in System A bridged to System B are shared. For example:

A <--> Bridge <--> B

Events that propagate in A, will propagate to B across the Bridge.
Events that propagate in B, will propagate to A across the Bridge.

When the Bridge is created, it will automatically attempt to send a
Helo Event to any configured nodes or on a broadcast address if no
nodes are initially configured. The default Bridge implementation
uses the UDP protocol and as such events cannot be guaranteed of their
order or delivery.
"""

from StringIO import StringIO
from pickle import dumps, Unpickler

from components import BaseComponent
from values import Value, ValueChanged
from events import Event, Registered, Unregistered, Started, Stopped

from circuits.net.sockets import Write

class Bridge(BaseComponent):

    IgnoreEvents = [Registered, Unregistered, Started, Stopped, ValueChanged]
    IgnoreChannels = [("*", "exception")]

    def __init__(self, manager, socket=None):
        super(Bridge, self).__init__()

        self._manager = manager
        self._socket = socket

        self._values = dict()

        self._manager.addHandler(self._started, "started", target="*")
        self._manager.addHandler(self._events, priority=100, target="*")
        self._manager.addHandler(self._value, "value", target=self._manager)

        if self._socket is not None:
            self._socket.register(self)
            self.addHandler(self._reader, "read", target=self._socket)

    def _started(self, component, mode):
        self.start()

    def _value(self, value):
        try:
            eid = self._values[value]
            s = dumps((eid, value), -1)
            self.push(Write(s), target=self._socket)
        except:
            return

    def _process(self, id, obj):
        if isinstance(obj, Event):
            obj.remote = True
            value = self._manager.push(obj)
            self._values[value] = id
            value.manager = self._manager
            value.onSet = "value",
        elif isinstance(obj, Value):
            self._values[id].value = obj.value

    def _reader(self, data):
        unpickler = Unpickler(StringIO(data))

        while True:
            try:
                self._process(*unpickler.load())
            except EOFError:
                break

    def _writer(self, event):
        try:
            eid = id(event)
            self._values[eid] = event.value
            s = dumps((eid, event))
            self.push(Write(s), target=self._socket)
        except:
            return

    def _events(self, event, *args, **kwargs):
        if True in [event.name == x.__name__ for x in self.IgnoreEvents]:
            return
        elif event.channel in self.IgnoreChannels:
            return
        elif getattr(event, "remote", False):
            return
        else:
            self._writer(event)
