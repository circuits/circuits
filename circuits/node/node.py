# Module:   node
# Date:     ...
# Author:   ...

"""Node

...
"""

from .events import Remote
from .client import Client
from .server import Server

from circuits import handler, BaseComponent, Event


class Node(BaseComponent):
    """Node

    ...
    """

    channel = "node"

    def __init__(self, bind, hosts, channel=channel):
        super(Node, self).__init__(channel=channel)

        self._hosts = []
        self._clients = []

        for i in range(hosts):
            client = Client(channel="%s.client%d" % (self.channel, i))
            client.register(self)
            self._clients.append(client)

        self._server = Server(bind, channel="%s.server" % self.channel)
        self._server.register(self)

    @handler(channel="*", priority=101.0)
    def _on_event(self, event, *args, **kwargs):
        print event
