# Module:   bridge
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Bridge

The Bridge Component is used for inter-process communications between
processes. Bridge is used internally when a Component is started in
"process mode" via :meth:`circuits.core.manager.start`. Typically a
Pipe is used as the socket transport between two sides of a Bridge
(*there must be a :class:`~Bridge` instnace on both sides*).

"""

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads  # NOQA

from .values import Value
from .events import Event
from .handlers import handler
from .components import BaseComponent


class Bridge(BaseComponent):

    channel = "bridge"

    ignore = [
        "registered", "unregistered", "started", "stopped", "error",
        "value_changed", "generate_events", "read", "write", "close",
        "connected", "connect", "disconnect", "disconnected", "_read",
        "_write"
    ]

    def init(self, socket, channel=channel):
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
            obj.notify = "value_changed"
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

        event.notify = "value_changed"
        self.send(event)
