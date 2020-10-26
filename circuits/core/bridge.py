"""Bridge

The Bridge Component is used for inter-process communications between
processes. Bridge is used internally when a Component is started in
"process mode" via :meth:`circuits.core.manager.start`. Typically a
Pipe is used as the socket transport between two sides of a Bridge
(*there must be a :class:`~Bridge` instnace on both sides*).
"""
import traceback

from ..six import b
from .components import BaseComponent
from .events import Event, exception
from .handlers import handler
from .values import Value

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads  # NOQA


_sentinel = b('~~~')


class ipc(Event):
    """ipc Event

    Send an event to a child/parent process
    """

    def __init__(self, event, channel=None):
        """
        :param event:   Event to execute remotely.
        :type event:    :class:`circuits.core.events.Event`

        :param channel: IPC Channel (channel to use on child/parent).
        :type channel:  str
        """

        super(ipc, self).__init__(event, channel=channel)


class Bridge(BaseComponent):

    channel = "bridge"

    def init(self, socket, channel=channel):
        self._buffer = b("")
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
            if value.errors:
                Bridge.__adapt_error_value(value)
            self.__write(eid, value)
        except Exception:
            pass

    @handler("read")
    def _on_read(self, data):
        self._buffer += data
        items = self._buffer.split(_sentinel)

        if items[-1] != "":
            self._buffer = items.pop()

        for item in filter(None, items):
            self._process_packet(*loads(item))

    def __send(self, eid, event):
        try:
            if isinstance(event, exception):
                Bridge.__adapt_exception(event)
            self._values[eid] = event.value
            self.__write(eid, event)
        except Exception:
            pass

    def __write(self, eid, data):
        self._socket.write(dumps((eid, data)) + _sentinel)

    @handler("ipc")
    def _on_ipc(self, event, ipc_event, channel=None):
        """Send event to a child/parentprocess

        Event handler to run an event on a child/parent process
        (the event definition is :class:`circuits.core.bridge.ipc`)

        :param event:    The event triggered (by the handler)
        :type event:     :class:`circuits.node.events.remote`

        :param ipc_event:    Event to execute in child/parent process.
        :type ipc_event:     :class:`circuits.core.events.Event`

        :param channel:    Remote channel (channel to use on peer).
        :type channel:     str

        :return: The result of remote event
        :rtype: generator

        :Example:
        ``# hello is your event to execute in the child process
        result = yield self.fire(ipc(hello()))
        print(result.value)``
        """

        ipc_event.channels = (channel,) if channel is not None else event.channels
        event.value.value = ipc_event.value = Value(ipc_event, self)

        eid = hash(ipc_event)
        self.__send(eid, ipc_event)
        yield self.wait(Bridge.__waiting_event(eid))

    @staticmethod
    def __waiting_event(eid):
        return '%s_done' % eid

    @staticmethod
    def __adapt_exception(ex):
        fevent_value = ex.kwargs['fevent'].value
        Bridge.__adapt_error_value(fevent_value)

    @staticmethod
    def __adapt_error_value(value):
        if not isinstance(value[2], list):
            value._value = (value[0], value[1], traceback.extract_tb(value[2]))
