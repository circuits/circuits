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

class Connect(Event):
    """Connect(host, port, ssl=False) -> Connect Event

    Connect event used for Client components to initiate a new connection.
    """

class Connected(Event):
    """Connected(Event) -> Connected Event

   if Client:
      - args: host, port

   if Server:
      - args: sock, host, port
   """

class Disconnected(Event):
    """Disconnected(Event) -> Disconnected Event

   if Client, no args.

   If Server:
      - args: sock
   """

class Read(Event):
    """Read(Event) -> Read Event

   if Client:
      - args: data

   If Server:
      - args: sock, data

   if UDP Client or Server:
      - args: address, data
   """

class Write(Event):
    """Write(Event) -> Write Event

   If Client:
      - args: data

   if Server:
      - args: sock, data

   if UDP Client or Server:
      - args: address, data
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
      - args: sock
    """

class Shutdown(Event):
    """Shutdown(Event) -> Shutdown Event

   If Client, no args.

   if Server:
      - args: sock
    """

class Client(Component):

    _connected = False

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

        self.host = ""
        self.port = 0
        self.ssl = False
        self.server = {}
        self.issuer = {}

        self._sock = None
        self._buffer = []
        self._socks = []
        self._read = []
        self._write = []
        self._close = False
        self._connected = False

    def __tick__(self):
        self.poll()

    @property
    def connected(self):
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

    def connect(self, host=None, port=None, ssl=None):
        self.host = host = (host if host is not None else self.host)
        self.port = port = (port if port is not None else self.port)
        self.ssl = ssl = (ssl if ssl is not None else self.ssl)

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
                self._read.append(self._sock)
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

    def __init__(self, host, port, ssl=False, bind=None, **kwargs):
        super(TCPClient, self).__init__(**kwargs)

        self.host = host
        self.port = port
        self.ssl = ssl
        self.bind = bind

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if bind is not None:
            self._sock.bind((bind, 0))

        self._socks.append(self._sock)

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
        try:
            r, w, _ = select.select(self._read, self._write, [], wait)
        except ValueError, ve:
            # Possibly a file descriptor has gone negative?
            return self._pruneSocks()
        except TypeError, te:
            # Something *totally* invalid (object w/o fileno, non-integral
            # result) was passed
            return self._pruneSocks()
        except (select.error, IOError), se:
            # select(2) encountered an error
            if se.args[0] in (0, 2):
                # windows does this if it got an empty list
                if (not self._reads) and (not self._writes):
                    return
                else:
                    raise
            elif se.args[0] == EINTR:
                return
            elif se.args[0] == EBADF:
                return self._pruneSocks()
            else:
                # OK, I really don't know what's going on.  Blow up.
                raise

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
                try:
                    newsock, host = self._sock.accept()
                except socket.error, e:
                    if e.args[0] in (EWOULDBLOCK, EAGAIN):
                        self.numberAccepts = i
                        return
                    elif e.args[0] == EPERM:
                        # Netfilter on Linux may have rejected the
                        # connection, but we get told to try to accept()
                        # anyway.
                        continue
                    elif e.args[0] in (EMFILE, ENOBUFS, ENFILE, ENOMEM, ECONNABORTED):

                        # Linux gives EMFILE when a process is not allowed
                        # to allocate any more file descriptors.  *BSD and
                        # Win32 give (WSA)ENOBUFS.  Linux can also give
                        # ENFILE if the system is out of inodes, or ENOMEM
                        # if there is insufficient memory to allocate a new
                        # dentry.  ECONNABORTED is documented as possible on
                        # both Linux and Windows, but it is not clear
                        # whether there are actually any circumstances under
                        # which it can happen (one might expect it to be
                        # possible if a client sends a FIN or RST after the
                        # server sends a SYN|ACK but before application code
                        # calls accept(2), however at least on Linux this
                        # _seems_ to be short-circuited by syncookies.

                        continue
                    raise
                newsock.setblocking(False)
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
