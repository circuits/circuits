# Module:   sockets
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""TCP/IP and UDP Sockets

This module contains classes for TCP/IP and UDP sockets for
both servers and clients. All classes are thin layers on-top
of the standard socket library. All implementations are
non-blocking. This module relies heavily on the event module
and as such the implementations in this module are all
event-driven and should be sub-classed to do something usefull.
"""

import errno
import socket

try:
    import select26 as select
except ImportError:
    import select

from circuits import listener, Event, Component

POLL_INTERVAL = 0.00001
CONNECT_TIMEOUT = 4
BUFFER_SIZE = 131072
BACKLOG = 512

###
### Events
###

class Connected(Event):
    """Connected(Event) -> Connected Event

   if Client:
      args: host, port

   if Server:
      args: sock, host, port
   """

class Disconnected(Event):
    """Disconnected(Event) -> Disconnected Event

   if Client, no args.

   If Server:
      args: sock
   """

class Read(Event):
    """Read(Event) -> Read Event

   if Client:
      args: data

   If Server:
      args: sock, data

   if UDP Client or Server:
      args: address, data
   """

class Write(Event):
    """Write(Event) -> Write Event

   If Client:
      args: data

   if Server:
      args: sock, data

   if UDP Client or Server:
      args: address, data
    """

class Error(Event):
    """Error(Event) -> Error Event

   if Client: error

   if Server: sock, error
   """

class Close(Event):
    """Close(Event) -> Close Event

   If Client, no args.

   if Server:
      args: sock
    """

class Shutdown(Event):
    """Shutdown(Event) -> Shutdown Event

   If Client, no args.

   if Server:
      args: sock
    """

class Client(Component):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

        self.host = ""
        self.port = 0
        self.ssl = False
        self.server = {}
        self.issuer = {}

        self._buffer = []
        self._socks = []
        self._read = []
        self._write = []
        self._close = False
        self._connected = False

    def __tick__(self):
        self.poll()

    def isConnected(self):
        return self._connected

    def poll(self, wait=POLL_INTERVAL):
        try:
            r, w, e = select.select(self._read, self._write, [], wait)
        except socket.error, error:
            if error[0] == errno.EBADF:
                self._connected = False
                return
        except select.error, error:
            if error[0] == 4:
                pass
            else:
                self.push(Error(error), "error", self.channel)
                return

        if r:
            try:
                if self.ssl and hasattr(self, "_ssock"):
                    data = self._ssock.read(BUFFER_SIZE)
                else:
                    data = self._sock.recv(BUFFER_SIZE)
                if data:
                    self.push(Read(data), "read", self.channel)
                else:
                    self.close()
                    return
            except socket.error, error:
                self.push(Error(error), "error", self.channel)
                self.close()
                return

        if w:
            if self._buffer:
                data = self._buffer[0]
                self.send(Write(data), "send", self.channel)
            else:
                if self._close:
                    self.close()
                else:
                    self._write.remove(self._sock)

    def open(self, host, port, ssl=False):
        self.ssl = ssl
        self.host = host
        self.port = port

        try:
            try:
                self._sock.connect((host, port))
            except socket.error, error:
                if error[0] == errno.EINPROGRESS:
                    pass

            if self.ssl:
                self._ssock = socket.ssl(self._sock)
            
            r, w, e = select.select([], self._socks, [], CONNECT_TIMEOUT)
            if w:
                self._connected = True
                self.push(Connected(host, port), "connected", self.channel)
            else:
                self.push(Error("Connection timed out"), "error", self.channel)
                self.close()
        except socket.error, error:
            self.push(Error(error), "error", self.channel)
            self.close()

    def close(self):
        if self._socks:
            self.send(Shutdown(), "shutdown", self.channel)

    def write(self, data):
        if not self._sock in self._write:
            self._write.append(self._sock)
        self._buffer.append(data)

    @listener("shutdown", type="filter")
    def onSHUTDOWN(self):
        """Close Event (Private)

        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        if self._buffer:
            self._close = True
            return

        try:
            self._sock.shutdown(2)
            self._sock.close()
            self.push(Disconnected(), "disconnected", self.channel)
        except socket.error, error:
            self.push(Error(error), "error", self.channel)
        finally:
            self._connected = False

            if self._sock in self._socks:
                self._socks.remove(self._sock)
            if self._sock in self._read:
                self._read.remove(self._sock)
            if self._sock in self._write:
                self._write.remove(self._sock)


class TCPClient(Client):

    def open(self, host, port, ssl=False, bind=None):
        self._sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if bind is not None:
            self._sock.bind((bind, 0))

        self._socks.append(self._sock)
        self._read.append(self._sock)

        super(TCPClient, self).open(host, port, ssl)

    @listener("send", type="filter")
    def onSEND(self, data):
        """Send Event

        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            if self.ssl:
                bytes = self._ssock.write(data)
            else:
                bytes = self._sock.send(data)

            if bytes < len(data):
                self._buffer[0] = data[bytes:]
            else:
                del self._buffer[0]
        except socket.error, error:
            if error[0] in [32, 107]:
                self.close()
            else:
                self.push(Error(error), "error", self.channel)
                self.close()


class Server(Component):

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

        self.address = ""
        self.port = 0
        self.ssl = False

        self._buffers = {}

        self._socks = []
        self._read = []
        self._write = []
        self._close = []

    def __getitem__(self, y):
        "x.__getitem__(y) <==> x[y]"

        return self._socks[y]

    def __contains__(self, y):
        "x.__contains__(y) <==> y in x"
    
        return y in self._socks

    def __tick__(self):
        self.poll()

    def poll(self, wait=POLL_INTERVAL):
        r, w, e = select.select(self._read, self._write, [], wait)

        for sock in w:
            if self._buffers[sock]:
                data = self._buffers[sock][0]
                self.send(Write(sock, data), "send", self.channel)
            else:
                if sock in self._close:
                    self.close(sock)
                else:
                    self._write.remove(sock)
            
        for sock in r:
            if sock == self._sock:
                newsock, host = sock.accept()
                newsock.setblocking(False)
                newsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._socks.append(newsock)
                self._read.append(newsock)
                self._buffers[newsock] = []
                self.push(Connected(newsock, *host), "connected", self.channel)
            else:
                try:
                    data = sock.recv(BUFFER_SIZE)
                    if data:
                        self.push(Read(sock, data), "read", self.channel)
                    else:
                        self.close(sock)
                except socket.error, e:
                    self.push(Error(sock, e), "error", self.channel)
                    self.close(sock)

    def close(self, sock=None):
        if sock in self:
            self.send(Shutdown(sock), "shutdown", self.channel)

    def write(self, sock, data):
        if not sock in self._write:
            self._write.append(sock)
        self._buffers[sock].append(data)

    def broadcast(self, data):
        for sock in self._socks[1:]:
            self.write(sock, data)

    @listener("send", type="filter")
    def onSEND(self, sock, data):
        """Send Event


        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            bytes = sock.send(data)
            if bytes < len(data):
                self._buffers[sock][0] = data[bytes:]
            else:
                del self._buffers[sock][0]
        except socket.error, e:
            if e[0] in [32, 107]:
                self.close(sock)
            else:
                self.push(Error(sock, e), "error", self.channel)
                self.close()

    @listener("shutdown", type="filter")
    def onSHUTDOWN(self, sock=None):
        """Close Event (Private)

        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        if sock:
            if sock not in self._socks:
                # Invalid/Closed socket
                return

            if not sock == self._sock:
                if self._buffers[sock]:
                    self._close.append(sock)
                    return

            try:
                sock.shutdown(2)
                sock.close()
                self.push(Disconnected(sock), "disconnect", self.channel)
            except socket.error, e:
                self.push(Error(sock, e), "error", self.channel)
            finally:
                if sock in self._socks:
                    self._socks.remove(sock)
                if sock in self._read:
                    self._read.remove(sock)
                if sock in self._write:
                    self._write.remove(sock)
                if sock in self._close:
                    self._close.remove(sock)
                if sock in self._buffers:
                    del self._buffers[sock]

        else:
            for sock in self._socks:
                self.close(sock)


class TCPServer(Server):

    def __init__(self, port, address="", **kwargs):
        super(TCPServer, self).__init__(**kwargs)

        self._sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self._sock.bind((address, port))
        self._sock.listen(BACKLOG)

        self._socks.append(self._sock)
        self._read.append(self._sock)

        self.address = address
        self.port = port

class UDPServer(Server):

    def __init__(self, port, address="", **kwargs):
        super(UDPServer, self).__init__(**kwargs)

        # Remove Inherited  Event Handler Server_onSEND
        self.manager._remove(self.Server_onSEND)
        del self.Server_onSEND

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET,    socket.SO_BROADCAST, 1)
        self._sock.setblocking(False)
        self._sock.bind((address, port))

        self._socks.append(self._sock)
        self._read = [self._sock]

        self.address = address
        self.port = port

    def poll(self, wait=POLL_INTERVAL):
        r, w, e = select.select(self._read, self._write, [], wait)

        if w:
            for address, data in self._buffers.iteritems():
                if data:
                    self.send(Write(address, data[0]), "send", self.channel)
                else:
                    if self._close:
                        self.close()
            self._write.remove(w[0])

        if r:
            try:
                data, address = self._sock.recvfrom(BUFFER_SIZE)

                if not data:
                    self.close()
                else:
                    self.push(Read(address, data), "read", self.channel)
            except socket.error, e:
                self.push(Error(self._sock, e), "error", self.channel)
                self.close()

    def write(self, address, data):
        if not self._write:
            self._write.append(self._sock)
        if not self._buffers.has_key(address):
            self._buffers[address] = []
        self._buffers[address].append(data)

    def broadcast(self, data):
        self.write("<broadcast", data)

    def close(self):
        if self._socks:
            self.send(Shutdown(), "shutdown", self.channel)

    @listener("shutdown", type="filter")
    def onSHUTDOWN(self):
        """Close Event (Private)

        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            self._socks.remove(self._sock)
            self._read.remove(self._sock)
            self._write.remove(self._sock)
            self._sock.shutdown(2)
            self._sock.close()
        except socket.error, error:
            self.push(Error(error), "error", self.channel)

    @listener("send", type="filter")
    def onSEND(self, address, data):
        """Send Event


        Typically this should NOT be overridden by sub-classes.
        If it is, this should be called by the sub-class first.
        """

        try:
            self._sock.sendto(data, address)
            del self._buffers[address][0]
        except socket.error, e:
            if e[0] in [32, 107]:
                self.close()
            else:
                self.push(Error(e), "error", self.channel)
                self.close()

UDPClient = UDPServer
