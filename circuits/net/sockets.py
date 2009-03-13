# Module:   sockets
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Socket Components

This module contains various Socket Components for use with Networking.
"""

import os
import socket
from errno import *
from collections import defaultdict, deque

from circuits.net.pollers import Select as DefaultPoller
from circuits.core import handler, Event, Component

TIMEOUT = 0.000001  # 0.001ms Poller Timeout
BUFSIZE = 4096      # 4KB Buffer
BACKLOG = 128       # 128 Concurrent Connections

###
### Event Objects
###

class Connect(Event):
    """Connect Event

    This Event is sent when a new client connection has arrived on a server.

    @param sock:   The socket of the new connecting client.
    @type  Socket: Socket

    @param host: The new client's hostname
    @type  str:  str

    @param port: The nwe client's connecting port.
    @type  int:  int
    """

    def __init__(self, sock, host, port):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Connect, self).__init__(sock, host, port)

class Disconnect(Event):
    """Disconnect Event

    This Event is sent when a client connection has closed on a server.

    @param sock:   The socket of the new connecting client.
    @type  Socket: Socket
    """

    def __init__(self, sock):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Disconnect, self).__init__(sock)

class Connected(Event):
    """Connected Event

    This Event is sent when a client has successfully connected.

    @note: This event is for Client Components.

    @param host: The hostname connected to.
    @type  str:  str

    @param port: The port connected to
    @type  int:  int
    """

    def __init__(self, host, port):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Connected, self).__init__(host, port)

class Disconnected(Event):
    """Disconnected Event

    This Event is sent when a client has disconnected

    @note: This event is for Client Components.
    """

    def __init__(self):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Disconnected, self).__init__()

class Read(Event):
    """Read Event

    This Event is sent when a client or server connection has read any data.

    @note: This event is used for both Client and Server Components.

    @param sock:   The socket of the client connection. (Server(s) only).
    @type  Socket: Socket (Server(s) only).

    @param data: The new data that was read for this client or connection.
    @type  str:  str
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Read, self).__init__(*args)

class Error(Event):
    """Error Event

    This Event is sent when a client or server connection has an error.

    @note: This event is used for both Client and Server Components.

    @param sock:   The socket of the client connection. (Server(s) only).
    @type  Socket: Socket (Server(s) only).

    @param error:         The socket error that occured.
    @type  socket.error:  socket.error
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(*args)

class Write(Event):
    """Write Event

    This Event is used to notify a client, client connection or server that
    we have data to be written.

    @hote: This event is never sent, it is used to send data.
    @note: This event is used for both Client and Server Components.

    @param sock:   The socket of the client connection to send data to.
                   (Server(s) only).
    @type  Socket: Socket (Server(s) only).
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Write, self).__init__(*args)


class Close(Event):
    """Close Event

    This Event is used to notify a client, client connection or server that
    we want to close.

    @hote: This event is never sent, it is used to close.
    @note: This event is used for both Client and Server Components.

    @param sock:   The socket of the client connection to close.
                   (Server(s) only).
    @type  Socket: Socket (Server(s) only).
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Write, self).__init__(*args)

###
### Components
###

class Client(Component):

    channel = "client"

    def __init__(self, bind=None, channel=channel, **kwargs):
        super(Client, self).__init__(channel=channel, **kwargs)

        self.bind = bind

        self.server = {}
        self.issuer = {}

        Poller = kwargs.get("poller", DefaultPoller)
        timeout = kwargs.get("timeout", TIMEOUT)

        self._poller = Poller(self, timeout)
        self._poller.register(self)

        self._sock = None
        self._sslsock = None
        self._buffer = deque()
        self._closeflag = False
        self._connected = False

    @property
    def connected(self):
        return getattr(self, "_connected", None)

    def _close(self):
        self._poller.discard(self._sock)

        self._buffer.clear()
        self._closeflag = False

        try:
            self._sock.shutdown(2)
            self._sock.close()
        except socket.error:
            pass

        self.push(Disconnected(), "disconnected", self.channel)

    def close(self):
        if not self._buffer:
            self._close()
        elif not self._closeflag:
            self._closeflag = True

    def _read(self):
        try:
            if self.ssl and self._sslsock:
                data = self._sslsock.read(BUFSIZE)
            else:
                data = self._sock.recv(BUFSIZE)

            if data:
                self.push(Read(data), "read", self.channel)
            else:
                self.close()
        except socket.error, e:
            self.push(Error(e), "error", self.channel)
            self._close()

    def _write(self, data):
        try:
            if self.ssl and self._sslsock:
                bytes = self._sslsock.write(data)
            else:
                bytes = self._sock.send(data)

            if bytes < len(data):
                self._buffer.appendleft(data[bytes:])
        except socket.error, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close(self._sock)
            else:
                self.push(Error(e), "error", self.channel)

    def write(self, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self._sock)
        self._buffer.append(data)

    @handler("_disconnect", filter=True)
    def __on_disconnect(self, sock):
        self.push(Disconnect(sock), "disconnect", self.channel)

    @handler("_read", filter=True)
    def __on_read(self, sock):
        self._read()

    @handler("_write", filter=True)
    def __on_write(self, sock):
        if self._buffer:
            data = self._buffer.popleft()
            self._write(data)

        if not self._buffer:
            if self._closeflag:
                self._close(self._sock)
            elif self._poller.isWriting(self._sock):
                self._poller.removeWriter(self._sock)

class TCPClient(Client):

    def __init__(self, bind=None, **kwargs):
        super(TCPClient, self).__init__(bind, **kwargs)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if bind is not None:
            self._sock.bind((bind, 0))

    def connect(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.ssl  = ssl

        try:
            r = self._sock.connect_ex((host, port))
        except socket.error, e:
            r = e[0]

        if r:
            if r == EISCONN:
                self._connected = True
            elif r in (EWOULDBLOCK, EINPROGRESS, EALREADY):
                self._connected = True
            else:
                self.push(Error(r), "error", self.channel)
                return

        self._connected = True

        self._poller.addReader(self._sock)

        if self.ssl:
            self._sslsock = socket.ssl(self._sock)
        
        self.push(Connected(host, port), "connected", self.channel)

class Server(Component):

    channel = "server"

    def __init__(self, bind, ssl=False, channel=channel, **kwargs):
        super(Server, self).__init__(channel=channel)

        self.bind = bind
        self.ssl = ssl

        Poller = kwargs.get("poller", DefaultPoller)
        timeout = kwargs.get("timeout", TIMEOUT)

        self._poller = Poller(self, timeout)
        self._poller.register(self)

        self._sock = None
        self._buffers = defaultdict(deque)
        self._closeq = []
        self._clients = []

    def _close(self, sock):
        if sock not in self._clients:
            return

        self._poller.discard(sock)

        if sock in self._buffers:
            del self._buffers[sock]

        if sock in self._clients:
            self._clients.remove(sock)

        try:
            sock.shutdown(2)
            sock.close()
        except socket.error:
            pass

        self.push(Disconnect(sock), "disconnect", self.channel)

    def close(self, sock=None):
        if not self._buffers[sock]:
            self._close(sock)
        elif sock not in self._closeq:
            self._closeq.append(sock)

    def _read(self, sock):
        if sock not in self._clients:
            return

        try:
            data = sock.recv(BUFSIZE)
            if data:
                self.push(Read(sock, data), "read", self.channel)
            else:
                self.close(sock)
        except socket.error, e:
            self.push(Error(sock, e), "error", self.channel)
            self._close(sock)

    def _write(self, sock, data):
        if sock not in self._clients:
            return

        try:
            bytes = sock.send(data)
            if bytes < len(data):
                self._buffers[sock].appendleft(data[bytes:])
        except socket.error, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close(sock)
            else:
                self.push(Error(sock, e), "error", self.channel)

    def write(self, sock, data):
        if not self._poller.isWriting(sock):
            self._poller.addWriter(sock)
        self._buffers[sock].append(data)

    def _accept(self):
        try:
            newsock, host = self._sock.accept()
        except socket.error, e:
            assert not e[0] == ECONNRESET
            if e[0] in (EWOULDBLOCK, EAGAIN):
                return
            elif e[0] == EPERM:
                # Netfilter on Linux may have rejected the
                # connection, but we get told to try to accept()
                # anyway.
                return
            elif e[0] in (EMFILE, ENOBUFS, ENFILE, ENOMEM, ECONNABORTED):
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
                return
            else:
                raise

        newsock.setblocking(False)
        self._poller.addReader(newsock)
        self._clients.append(newsock)
        self.push(Connect(newsock, *host), "connect", self.channel)

    @handler("_disconnect", filter=True)
    def _on_disconnect(self, sock):
        self.push(Disconnect(sock), "disconnect", self.channel)

    @handler("_read", filter=True)
    def _on_read(self, sock):
        if sock == self._sock:
            self._accept()
        else:
            self._read(sock)

    @handler("_write", filter=True)
    def _on_write(self, sock):
        if self._buffers[sock]:
            data = self._buffers[sock].popleft()
            self._write(sock, data)

        if not self._buffers[sock]:
            if sock in self._closeq:
                self._closeq.remove(sock)
                self._close(sock)
            elif self._poller.isWriting(sock):
                self._poller.removeWriter(sock)

class TCPServer(Server):

    def __init__(self, bind, ssl=False, **kwargs):
        super(TCPServer, self).__init__(bind, ssl, **kwargs)

        oldUmask = None
        if type(bind) == str:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                os.unlink(self.bind)
            except OSError:
                pass
            umask = kwargs.get("umask", None)
            if umask:
                oldUmask = os.umask(umask)
        else:
            if type(bind) is int:
                self.bind = ("0.0.0.0", self.bind)
            else:
                assert type(self.bind) is tuple

            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self._sock.bind(self.bind)
        self._sock.listen(BACKLOG)

        self._poller.addReader(self._sock)

        if oldUmask is not None:
            os.umask(oldUmask)

class UDPServer(Server):

    def __init__(self, port, address="", ssl=False, **kwargs):
        super(UDPServer, self).__init__(port, address, ssl, **kwargs)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.setblocking(False)
        self._sock.bind((address, port))

        self._poller.addReader(self._sock)

    def _close(self):
        self._poller.discard(self._sock)

        if self._sock in self._buffers:
            del self._buffers[sock]

        try:
            sock.shutdown(2)
            sock.close()
        except socket.error:
            pass

        self.push(Disconnect(sock), "disconnect", self.channel)

    @handler("close", override=True)
    def close(self):
        if self._sock not in self._closeq:
            self._closeq.append(self._sock)

    def _read(self):
        try:
            data, address = self._sock.recvfrom(BUFSIZE)
            if data:
                self.push(Read(address, data), "read", self.channel)
            else:
                self.close(self._sock)
        except socket.error, e:
            self.push(Error(self._sock, e), "error", self.channel)
            self._close(self._sock)

    def _write(self, address, data):
        try:
            print repr(address), repr(data)
            self._sock.sendto(data, address)
        except socket.error, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close(self._sock)
            else:
                self.push(Error(self._sock, e), "error", self.channel)

    @handler("write", override=True)
    def write(self, address, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self._sock)
        self._buffers[self._sock].append((address, data))

    def broadcast(self, data):
        self.write("<broadcast>", data)

    @handler("_disconnect", filter=True, override=True)
    def _on_disconnect(self, sock):
        self.push(Disconnected(), "disconnected", self.channel)

    @handler("_read", filter=True, override=True)
    def _on_read(self, sock):
        self._read()

    @handler("_write", filter=True, override=True)
    def _on_write(self, sock):
        if self._buffers[self._sock]:
            address, data = self._buffers[self._sock].popleft()
            self._write(address, data)

        if not self._buffers[self._sock]:
            if self._sock in self._closeq:
                self._closeq.remove(self._sock)
                self._close(self._sock)
            elif self._poller.isWriting(self._sock):
                self._poller.removeWriter(self._sock)

UDPClient = UDPServer


