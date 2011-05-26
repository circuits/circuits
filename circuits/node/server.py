# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""

from circuits import handler, BaseComponent, Event
from circuits.net.sockets import Close, TCPServer, Write

from .utils import load_event

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
        e, id = load_event(packet)

        name = "%s_value_changed" % e.name
        channel = e.channels[0] if e.channels else self
        
        @handler(name, channel=channel)
        def on_value_changed(self, value):
            self.send(value)

        self._handlers.setdefault(name, set()).add(on_value_changed)

        v = self.fire(e, *e.channels)
        v.notify = True

    def send(self, v):
        data = v.dumps()
        self.fire(Write("V%s%s" % (data, DELIMITER)))

    @handler("read")
    def _on_read(self, sock, data):
        buffer = self._buffers.get(sock, "")

        buffer += data

        delimiter = buffer.find(DELIMITER)
        if delimiter > 0:
            packet = buffer[:delimiter]
            self._buffers[sock] = buffer[(delimiter + len(DELIMITER)):]
            self.process(packet)
