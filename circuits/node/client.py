# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

from weakref import WeakValueDictionary

from circuits import handler, BaseComponent
from circuits.net.sockets import Close, Connect, TCPClient, Write

from .utils import dump_event, load_value

DELIMITER = "\r\n\r\n"


class Client(BaseComponent):
    """Client

    ...
    """

    channel = "node"

    def __init__(self, host, port, channel=channel):
        super(Client, self).__init__(channel=channel)

        self._host = host
        self._port = port

        self._nid = 0
        self._buffer = ""
        self._values = WeakValueDictionary()

        TCPClient(channel=self.channel).register(self)
        self.fire(Connect(self._host, self._port))

    def process(self, packet):
        v, id, errors = load_value(packet)

        if id in self._values:
            value = self._values[id]
            value.value = v
            value.errors = errors

    def close(self):
        self.fire(Close())

    def connect(self, host, port):
        self.fire(Connect(host, port))

    def send(self, event, e):
        id = self._nid
        self._nid += 1

        self._values[id] = event.value
        data = dump_event(e, id)

        self.fire(Write("%s%s" % (data, DELIMITER)))

    @handler("read")
    def _on_read(self, data):
        self._buffer += data

        delimiter = self._buffer.find(DELIMITER)
        if delimiter > 0:
            packet = self._buffer[:delimiter]
            self._buffer = self._buffer[(delimiter + len(DELIMITER)):]
            self.process(packet)
