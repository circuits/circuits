# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

from weakref import WeakValueDictionary

from circuits.net.sockets import TCPClient
from circuits import handler, BaseComponent
from circuits.net.events import close, connect, write

from .utils import dump_event, load_value

DELIMITER = b"\r\n\r\n"


class Client(BaseComponent):
    """Client

    ...
    """

    channel = "node"

    def __init__(self, host, port, channel=channel, **kwargs):
        super(Client, self).__init__(channel=channel, **kwargs)

        self._host = host
        self._port = port

        self._nid = 0
        self._buffer = b""
        self._values = {}

        TCPClient(channel=self.channel, **kwargs).register(self)

    @handler("ready")
    def _on_ready(self, component):
        self.fire(connect(self._host, self._port))

    def _process_packet(self, packet):
        value, id, errors = load_value(packet)

        if id in self._values:
            self._values[id].value = value
            self._values[id].errors = errors

    def close(self):
        self.fire(close())

    def connect(self, host, port):
        self.fire(connect(host, port))

    def send(self, event, e):
        id = self._nid
        self._nid += 1

        self._values[id] = event.value
        data = dump_event(e, id)
        packet = data.encode("utf-8") + DELIMITER

        self.fire(write(packet))

        while not self._values[id].result:
            yield

        del(self._values[id])

    @handler("read")
    def _on_read(self, data):
        self._buffer += data

        delimiter = self._buffer.find(DELIMITER)
        if delimiter > 0:
            packet = self._buffer[:delimiter].decode("utf-8")
            self._buffer = self._buffer[(delimiter + len(DELIMITER)):]
            self._process_packet(packet)
