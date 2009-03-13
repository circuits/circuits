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

import socket
import select
from cPickle import dumps as pickle
from cPickle import loads as unpickle
from socket import gethostname, gethostbyname

from circuits import handler, Event, Component


POLL_INTERVAL = 0.00001
BUFFER_SIZE = 131072


class Read(Event): pass
class Helo(Event): pass
class Error(Event): pass
class Write(Event): pass
class Close(Event): pass


class Bridge(Component):

    IgnoreEvents = ["Read", "Write"]
    IgnoreChannels = []

    def __init__(self, port, address="", nodes=[], *args, **kwargs):
        super(Bridge, self).__init__(*args, **kwargs)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET,    socket.SO_BROADCAST, 1)
        self._sock.setblocking(False)
        self._sock.bind((address, port))

        self._write = []
        self._buffers = {}
        self._read = [self._sock]

        self.address = address
        self.port = port

        self.nodes = set(nodes)

        if self.address in ["", "0.0.0.0"]:
            address = gethostbyname(gethostname())
        else:
            address = self.address

        self.ourself = (address, self.port)

    def registered(self, component, manager):
        self.push(Helo(*self.ourself), "helo")

    def __write__(self, address, data):
        if not self._write:
            self._write.append(self._sock)
        if not self._buffers.has_key(address):
            self._buffers[address] = []
        self._buffers[address].append(data)

    def __close__(self):
        self.push(Close(), "close", self.channel)

    def __tick__(self):
        self.poll()

    def poll(self, wait=POLL_INTERVAL):
        r, w, e = select.select(self._read, self._write, [], wait)

        if w:
            for address, data in self._buffers.iteritems():
                if data:
                    self.send(Write(address, data[0]), "write", self.channel)
            self._write.remove(w[0])

        if r:
            try:
                data, address = self._sock.recvfrom(BUFFER_SIZE)

                if not data:
                    self.__close__()
                else:
                    self.push(Read(address, data), "read", self.channel)
            except socket.error, e:
                self.push(Error(self._sock, e), "error", self.channel)
                self.__close__()

    @handler(filter=True)
    def onEVENTS(self, event, *args, **kwargs):
        channel = event.channel
        if True in [event.name == name for name in self.IgnoreEvents]:
            return
        elif channel in self.IgnoreChannels:
            return
        elif hasattr(event, "ignore") and event.ignore:
            return
        else:
            event.ignore = True

        event.source = self.ourself
        try:
            s = pickle(event, -1)
        except:
            return

        if self.nodes:
            for node in self.nodes:
                self.__write__(node, s)
        else:
            self.__write__(("<broadcast>", self.port), s)

    @handler("helo", filter=True)
    def onHELO(self, event, address, port):
        source = event.source

        if (address, port) == self.ourself or source in self.nodes:
            return True

        if not (address, port) in self.nodes:
            self.nodes.add((address, port))
            self.push(Helo(*self.ourself), "helo")

    @handler("read", filter=True)
    def onREAD(self, address, data):
        event = unpickle(data)

        channel = event.channel
        target = event.target
        source = event.source

        if source == self.ourself:
            return

        self.send(event, channel, target)

    @handler("close", filter=True)
    def onCLOSE(self):
        """Close Event

        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            self._read.remove(self._sock)
            self._write.remove(self._sock)
            self._sock.shutdown(2)
            self._sock.close()
        except socket.error, error:
            self.push(Error(error), "error", self.channel)

    @handler("write", filter=True)
    def onWRITE(self, address, data):
        """Write Event


        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            self._sock.sendto(data, address)
            del self._buffers[address][0]
        except socket.error, e:
            if e[0] in [32, 107]:
                self.__close__()
            else:
                self.push(Error(e), "error", self.channel)
                self.__close__()

