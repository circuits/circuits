# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""

from circuits.core import Value

from circuits.net.events import write
from circuits.net.sockets import TCPServer
from circuits import handler, BaseComponent, Event

from .utils import load_event, dump_value

DELIMITER = b"\r\n\r\n"


class Server(BaseComponent):
    """Server

    ...
    """

    channel = "node"

    def __init__(self, bind, channel=channel, **kwargs):
        super(Server, self).__init__(channel=channel, **kwargs)

        self._buffers = {}
        self.__server_event_firewall = kwargs.get(
            'server_event_firewall',
            None
        )

        self.transport = TCPServer(bind, channel=self.channel, **kwargs).register(self)

    @handler('_process_packet')
    def _process_packet(self, sock, packet):
        event, id = load_event(packet)

        if self.__server_event_firewall and \
                not self.__server_event_firewall(event, sock):
            value = Value(event, self)

        else:
            value = yield self.call(event, *event.channels)

        value.notify = True
        value.node_trn = id
        value.node_sock = sock
        self.send(value)

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
            self.fire(Event.create('_process_packet', sock, packet))

    @property
    def host(self):
        if hasattr(self, "transport"):
            return self.transport.host

    @property
    def port(self):
        if hasattr(self, "transport"):
            return self.transport.port
