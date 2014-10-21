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
import traceback

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads  # NOQA

from .values import Value
from .events import Event, exception
from .handlers import handler
from .components import BaseComponent
from ..six import b


_sentinel = b('~~~')


class Bridge(BaseComponent):

    channel = "bridge"

    ignore = [
        "registered", "unregistered", "started", "stopped", "error",
        "value_changed", "generate_events", "read", "write", "close",
        "connected", "connect", "disconnect", "disconnected", "_read",
        "_write", "ready", "read_value_changed", "prepare_unregister"
    ]

    def init(self, socket, channel=channel):
        self._socket = socket
        self._values = dict()

        if self._socket is not None:
            self._socket.register(self)

    def _process_packet(self, eid, obj):
        if isinstance(obj, Event):
            obj.remote = True
            obj.notify = "value_changed"
            obj.waitingHandlers = 0
            value = self.fire(obj)
            self._values[value] = eid
        elif isinstance(obj, Value):
            if obj.result:
                if isinstance(obj.value, list):
                    for item in obj.value:
                        self._values[eid].value = item
                else:
                    self._values[eid].value = obj.value
            event = Event.create(Bridge.__waiting_event(eid))
            event.remote = True
            self.fire(event, self.channel)


    @handler("value_changed", channel="*")
    def _on_value_changed(self, value):
        try:
            eid = self._values[value]
            self.__write(eid, value)
        except:
            pass

    @handler("read")
    def _on_read(self, data):
        data = data.split(_sentinel)
        for item in data[:-1]:
            self._process_packet(*loads(item))

    def send(self, eid, event):
        try:
            if isinstance(event, exception):
                Bridge.__adapt_exception(event)
            self._values[eid] = event.value
            self.__write(eid, event)
        except:
            pass

    def __write(self, eid, data):
        self._socket.write(dumps((eid, data))+_sentinel)

    @handler(channel="*", priority=100.0)
    def _on_event(self, event, *args, **kwargs):
        if event.name in self.ignore or getattr(event, "remote", False) \
                or event.name.endswith('_done') \
                or event.name.endswith('_success') \
                or event.name.endswith('_complete'):
            return

        eid = hash(event)
        self.send(eid, event)
        yield self.wait(Bridge.__waiting_event(eid))

    @staticmethod
    def __waiting_event(eid):
        return '%s_done' % eid

    @staticmethod
    def __adapt_exception(ex):
        fevent_value = ex.kwargs['fevent'].value
        fevent_value._value = (fevent_value[0], fevent_value[1], traceback.extract_tb(fevent_value[2]))
