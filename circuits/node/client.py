# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

from circuits import handler, BaseComponent
from circuits.net.sockets import Close, Connect, TCPClient, Write

from .events import Packet


class Client(BaseComponent):
    """Client

    ...
    """

    channel = "node.client"

    def __init__(self, channel=channel):
        super(Client, self).__init__(channel=channel)

        TCPClient(channel=self.channel).register(self)

    def close(self):
        self.fire(Close())

    def connect(self, host, port):
        self.fire(Connect(host, port))

    def write(self, data):
        self.fire(Write(data))

    @handler("read")
    def _on_read(self, data):
        self.fire(Packet(data), self.parent)
