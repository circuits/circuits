# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

from circuits.net.sockets import TCPClient
from circuits import handler, BaseComponent
from circuits.net.events import close, connect

from .protocol import Protocol


class Client(BaseComponent):
    """Client

    ...
    """

    channel = "node"

    def __init__(self, host, port, channel=channel,
                 receive_event_firewall=None, send_event_firewall=None,
                 **kwargs):
        super(Client, self).__init__(channel=channel, **kwargs)

        self._host = host
        self._port = port
        self._protocol = Protocol(
            receive_event_firewall=receive_event_firewall,
            send_event_firewall=send_event_firewall,
            channel=channel
        ).register(self)

        TCPClient(channel=channel, **kwargs).register(self)

    @handler("ready")
    def _on_ready(self, component):
        self.fire(connect(self._host, self._port))

    def close(self):
        self.fire(close())

    def connect(self, host, port):
        self.fire(connect(host, port))

    def send(self, event, e):
        return self._protocol.send(e)

    @handler("read")
    def _on_read(self, data):
        self._protocol.add_buffer(data)
