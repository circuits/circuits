# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

from circuits import handler, BaseComponent
from circuits.net.sockets import Close, Connect, TCPClient, Write

from .events import Packet

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
        self._buffer = ""

        TCPClient(channel=self.channel).register(self)
        self.fire(Connect(self._host, self._port))

    def process(self, packet):
        v = load_value(packet)
        # XXX: ...

    def close(self):
        self.fire(Close())

    def connect(self, host, port):
        self.fire(Connect(host, port))

    def send(self, e):
        self._values[e] = e.value
        data = e.dumps()
        self.fire(Write("%s%s" % (data, DELIMITER)))

    @handler("read")
    def _on_read(self, data):
        self._buffer += data

        delimiter = self._buffer.find(DELIMITER)
        if delimiter > 0:
            packet = self._buffer[:delimiter]
            self._buffer = self._buffer[(delimiter + len(DELIMITER)):]
            self.process(packet)
