# Module:   bridge
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Bridge

Bridge Component to Bridge one or more components in a single System.
That is, events in System A bridged to System B are shared. For example:

A <--> Bridge <--> B

Events that propagate in A, will propagate to B across the Bridge.
Events that propagate in B, will propagate to A across the Bridge.

When the Bridge is created, it will automatically attempt to send a
Helo Event to any configured nodes or on a broadcast address if no
nodes are initially configured. The default Bridge implementation
uses the UDP protocol and as such events cannot be guaranteed of their
order or delivery.
"""

from cPickle import dumps, loads
from socket import gethostname, gethostbyname

from circuits import handler, Event, Component
from circuits.net.sockets import Client, Server, UDPServer as DefaultTransport
from circuits.net.sockets import Read, Write, Error, Close

class Helo(Event): pass

class Bridge(Component):

    channel = "bridge"

    IgnoreEvents = [Read, Write, Error, Close]
    IgnoreChannels = []

    def __init__(self, nodes=[], transport=None, **kwargs):
        super(Bridge, self).__init__(**kwargs)

        self.nodes = set(nodes)

        if transport:
            self.transport = transport
        else:
            self.transport = DefaultTransport(**kwargs)


        if isinstance(self.transport, DefaultTransport):
            self.write = self.udp
        elif isinstance(self.transport, Server):
            self.write = self.server
        elif isinstance(self.transport, Client):
            self.write = self.client
        else:
            raise TypeError("Unsupported transport type")

        if isinstance(self.transport, Client):
            self.server = False
        else:
            self.server = True

        self += self.transport

        if hasattr(self.transport, "address"):
            if self.transport.address in ["", "0.0.0.0"]:
                address = gethostbyname(gethostname())
                self.ourself = (address, self.transport.port)
            else:
                self.ourself = self.transport.bind
        else:
            self.ourself = (gethostbyname(gethostname()), 0)

    def registered(self, c, m):
        if c == self:
            self.push(Helo(*self.ourself), "helo")

    @handler(filter=True, priority=100)
    def event(self, event, *args, **kwargs):
        channel = event.channel
        if True in [event.name == x.__name__ for x in self.IgnoreEvents]:
            return
        elif channel in self.IgnoreChannels:
            return
        elif getattr(event, "ignore", False):
            return
        else:
            event.ignore = True

        event.source = self.ourself

        try:
            s = dumps(event, -1) + "\x00\x00"
        except:
            return

        self.write(channel, event, s)

    def udp(self, channel, e, s):
        if self.nodes:
            for node in self.nodes:
                self.transport.write(node, s)
        else:
            target, channel = channel
            if type(target) is tuple:
                if type(target[0]) is int:
                    node = ("<broadcast>", target[0])
                elif type(target[0]) is str and ":" in target[0]:
                    address, port = target[0].split(":", 1)
                    port = int(port)
                    node = (address, port)
                elif type(target[0]) is str:
                    node = (target[0], self.transport.port)
                elif type(target[0]) is int:
                    node = (self.transport.address, target[0])
                else:
                    raise TypeError("Invalid bridge target!")
            else:
                node = ("<broadcast>", self.transport.port)

            self.transport.write(node, s)

    def server(self, channel, e, s):
        self.transport.broadcast(s)

    def client(self, channel, e, s):
        self.transport.write(s)

    @handler("helo", filter=True)
    def helo(self, event, address, port):
        source = event.source

        if (address, port) == self.ourself or source in self.nodes:
            return True

        if not (address, port) in self.nodes:
            self.nodes.add((address, port))
            self.push(Helo(*self.ourself))

    def read(self, *args):
        if len(args) == 1: data = args[0]
        else: data = args[1]
        data = data.split("\x00\x00")
        for d in data:
            if d:
                self.push_event(loads(d))

    def push_event(self, event):
        (target, channel) = event.channel
        source = event.source

        if type(target) is tuple:
            if len(target) == 2:
                target = target[1]
            else:
                target = "*"

        self.send(event, channel, target)
