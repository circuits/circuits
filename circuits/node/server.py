# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""

from circuits.core.events import loads
from circuits import handler, BaseComponent, Event
from circuits.net.sockets import Close, TCPServer, Write

DELIMITER = "\r\n\r\n"


class Server(BaseComponent):
    """Server

    ...
    """

    channel = "node"

    def __init__(self, bind, channel=channel):
        super(Server, self).__init__(channel=channel)

        self._buffers = {}

        TCPServer(bind, channel=self.channel).register(self)

    def process(self, packet):
        e = loads(packet)
        self.fire(e, *e.channels)

    @handler("read")
    def _on_read(self, sock, data):
        buffer = self._buffers.get(sock, "")

        buffer += data

        delimiter = buffer.find(DELIMITER)
        if delimiter > 0:
            packet = buffer[:delimiter]
            self._buffers[sock] = buffer[(delimiter + len(DELIMITER)):]
            self.process(packet)
