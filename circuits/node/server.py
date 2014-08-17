# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""

from circuits.net.events import write
from circuits.net.sockets import TCPServer
from circuits import handler, BaseComponent

from .utils import load_event, dump_value

DELIMITER = b"\r\n\r\n"


class Server(BaseComponent):
    """Server

    ...
    """

    channel = "node"

    def __init__(self, bind, channel=channel):
        super(Server, self).__init__(channel=channel)

        self._buffers = {}

        self.transport = TCPServer(bind, channel=self.channel).register(self)

    def _process_packet(self, sock, packet):
        e, id = load_event(packet)

        name = "%s_value_changed" % e.name

        @handler(name, channel=self)
        def on_value_changed(self, event, value):
            self.send(value)

        self.addHandler(on_value_changed)

        v = self.fire(e, *e.channels)
        v.notify = True
        v.node_trn = id
        v.node_sock = sock

    def send(self, v):
        data = dump_value(v)
        packet = data.encode("utf-8") + DELIMITER
        self.fire(write(v.node_sock, packet))

    @handler("read")
    def _on_read(self, sock, data):
        buffer = self._buffers.get(sock, b"")

        buffer += data

        delimiter = buffer.find(DELIMITER)
        if delimiter > 0:
            packet = buffer[:delimiter].decode("utf-8")
            self._buffers[sock] = buffer[(delimiter + len(DELIMITER)):]
            self._process_packet(sock, packet)

    @property
    def host(self):
        if hasattr(self, "transport"):
            return self.transport.host

    @property
    def port(self):
        if hasattr(self, "transport"):
            return self.transport.port
