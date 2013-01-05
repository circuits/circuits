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

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO  # NOQA

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads  # NOQA

from .values import Value
from .events import Event
from .handlers import handler
from .components import BaseComponent


class Bridge(BaseComponent):

    ignore = [
        "registered", "unregistered", "started", "stopped", "error",
        "value_changed", "generate_events", "read", "write", "close",
        "connected", "connect", "disconnect", "disconnected"
    ]

    def init(self, socket):
        self._socket = socket
        self._values = dict()

        if self._socket is not None:
            self._socket.register(self)
            self.addHandler(
                handler("read", channel=self._socket.channel)(
                    self.__class__._on_read
                )
            )

    def _process_packet(self, eid, obj):
        if isinstance(obj, Event):
            obj.remote = True
            obj.notify = "ValueChanged"
            value = self.fire(obj)
            self._values[value] = eid
        elif isinstance(obj, Value):
            self._values[eid].value = obj.value

    @handler("value_changed", channel="*")
    def _on_value_changed(self, value):
        try:
            eid = self._values[value]
            self._socket.write(dumps((eid, value)))
        except:
            pass

    @staticmethod
    def _on_read(self, data):
        self._process_packet(*loads(data))

    def send(self, event):
        try:
            eid = hash(event)
            self._values[eid] = event.value
            self._socket.write(dumps((eid, event)))
        except:
            pass

    @handler(channel="*", priority=100.0)
    def _on_event(self, event, *args, **kwargs):
        if event.name in self.ignore or getattr(event, "remote", False):
            return

        event.notify = "ValueChanged"
        self.send(event)
