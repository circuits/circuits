# Module:   node
# Date:     ...
# Author:   ...

"""Node

...
"""

from hashlib import sha256

from .client import Client
from .server import Server

from circuits import handler, BaseComponent


class Node(BaseComponent):
    """Node

    ...
    """

    channel = "node"

    def __init__(self, bind=None, channel=channel, **kwargs):
        super(Node, self).__init__(channel=channel, **kwargs)

        self.bind = bind

        self.nodes = {}

        if self.bind is not None:
            self.server = Server(
                self.bind,
                channel=channel,
                **kwargs
            ).register(self)
        else:
            self.server = None

    def add(self, name, host, port, **kwargs):
        channel = sha256(
            "{0:s}:{1:d}".format(host, port).encode("utf-8")
        ).hexdigest()
        node = Client(host, port, channel=channel, **kwargs)
        node.register(self)

        self.nodes[name] = node

    @handler("remote")
    def _on_remote(self, event, e, name, channel=None):
        node = self.nodes[name]
        if channel is not None:
            e.channels = (channel,)
        return node.send(event, e)
