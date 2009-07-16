# Module:   sockets
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Socket Components

This module contains various Socket Components for use with Networking.
"""

import os
import socket
from errno import *
from _socket import socket as SocketType
from collections import defaultdict, deque
from socket import gethostname, gethostbyname

from circuits.net.pollers import Select as DefaultPoller
from circuits.core import handler, Event, Component

BUFSIZE = 4096 # 4KB Buffer
BACKLOG = 128  # 128 Concurrent Connections

###
### Event Objects
###

class Connect(Event):
    """Connect Event

    This Event is sent when a new client connection has arrived on a server.
    This event is also used for client's to initiate a new connection to
    a remote host.

    @note: This event is used for both Client and Server Components.

    @param args:  Client: (host, port) Server: (sock, host, port)
    @type  args: tuple

    @param kwargs: Client: (ssl)
    @type  kwargs: dict
    """

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Connect, self).__init__(*args, **kwargs)

class Disconnect(Event):
    """Disconnect Event

    This Event is sent when a client connection has closed on a server.
    This event is also used for client's to disconnect from a remote host.

    @note: This event is used for both Client and Server Components.

    @param args:  Client: () Server: (sock)
    @type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Disconnect, self).__init__(*args)

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

    @param args:  Client: (data) Server: (sock, data)
    @type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Read, self).__init__(*args)

class Error(Event):
    """Error Event

    This Event is sent when a client or server connection has an error.

    @note: This event is used for both Client and Server Components.

    @param args:  Client: (error) Server: (sock, error)
    @type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Error, self).__init__(*args)

class Write(Event):
    """Write Event

    This Event is used to notify a client, client connection or server that
    we have data to be written.

    @note: This event is never sent, it is used to send data.
    @note: This event is used for both Client and Server Components.

    @param args:  Client: (data) Server: (sock, data)
    @type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Write, self).__init__(*args)


class Close(Event):
    """Close Event

    This Event is used to notify a client, client connection or server that
    we want to close.

    @note: This event is never sent, it is used to close.
    @note: This event is used for both Client and Server Components.

    @param args:  Client: () Server: (sock)
    @type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Close, self).__init__(*args)

###
### Components
###

class Client(Component):

    channel = "client"

    def __init__(self, bind=None, channel=channel, **kwargs):
        super(Client, self).__init__(channel=channel, **kwargs)

        if type(bind) is int:
            self.bind = (gethostbyname(gethostname()), bind)
        elif type(bind) is str and ":" in bind:
            host, port = bind.split(":")
            port = int(port)
            self.bind = (host, port)
        else:
            self.bind = bind

        self.host = "0.0.0.0"
        self.port = 0
        self.ssl  = False

        self.server = {}
        self.issuer = {}

        self._bufsize = kwargs.get("bufsize", BUFSIZE)

        Poller = kwargs.get("poller", DefaultPoller)

        self._poller = Poller()
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
                data = self._sslsock.read(self._bufsize)
            else:
                data = self._sock.recv(self._bufsize)

            if data:
                self.push(Read(data), "read", self.channel)
            else:
                self.close()
        except socket.error, e:
            if e[0] == EWOULDBLOCK:
                return
            else:
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
                self._close()
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
                self._close()
            elif self._poller.isWriting(self._sock):
                self._poller.removeWriter(self._sock)

class TCPClient(Client):

    def __init__(self, bind=None, **kwargs):
        super(TCPClient, self).__init__(bind, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if bind is not None:
                self._sock.bind((bind, 0))

        self._sock.setblocking(False)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

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

class UNIXClient(Client):

    def __init__(self, bind=None, **kwargs):
        super(UNIXClient, self).__init__(bind, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if bind is not None:
                self._sock.bind(bind)

        self._sock.setblocking(False)

    def connect(self, path, ssl=False):
        self.path = path
        self.ssl = ssl

        try:
            r = self._sock.connect_ex(path)
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
        
        self.push(Connected(gethostname(), path), "connected", self.channel)


class Server(Component):

    channel = "server"

    def __init__(self, bind, ssl=False, channel=channel, **kwargs):
        super(Server, self).__init__(channel=channel)

        if type(bind) is int:
            self.bind = (gethostbyname(gethostname()), bind)
        elif type(bind) is str and ":" in bind:
            host, port = bind.split(":")
            port = int(port)
            self.bind = (host, port)
        else:
            self.bind = bind

        self.ssl = ssl

        self._bufsize = kwargs.get("bufsize", BUFSIZE)
        self._backlog = kwargs.get("backlog", BACKLOG)

        Poller = kwargs.get("poller", DefaultPoller)

        self._poller = Poller()
        self._poller.register(self)

        self._sock = None
        self._buffers = defaultdict(deque)
        self._closeq = []
        self._clients = []

    @property
    def connected(self):
        return True

    @property
    def address(self):
        return self.bind[0] if hasattr(self, "bind") else None

    @property
    def port(self):
        return self.bind[1] if hasattr(self, "bind") else None

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
            data = sock.recv(self._bufsize)
            if data:
                self.push(Read(sock, data), "read", self.channel)
            else:
                self.close(sock)
        except socket.error, e:
            if e[0] == EWOULDBLOCK:
                return
            else:
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

    def broadcast(self, data):
        for sock in self._clients:
            self.write(sock, data)

    def _accept(self):
        try:
            newsock, host = self._sock.accept()
        except socket.error, e:
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

        bound = False
        if type(bind) is SocketType:
            self._sock = bind
            bound = True
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._sock.setblocking(False)
        if not bound:
            print type(self.bind), repr(self.bind)
            self._sock.bind(self.bind)
        self._sock.listen(self._backlog)

        self._poller.addReader(self._sock)

class UNIXServer(Server):

    def __init__(self, bind, ssl=False, **kwargs):
        super(UNIXServer, self).__init__(bind, ssl, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            if os.path.exists(bind):
                os.unlink(self.bind)

            oldUmask = None
            umask = kwargs.get("umask", None)
            if umask:
                oldUmask = os.umask(umask)

            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.bind(self.bind)

            if oldUmask is not None:
                os.umask(oldUmask)

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)
        self._sock.listen(self._backlog)

        self._poller.addReader(self._sock)

class UDPServer(Server):

    def __init__(self, bind, ssl=False, **kwargs):
        super(UDPServer, self).__init__(bind, ssl, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.bind(self.bind)

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.setblocking(False)

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
            data, address = self._sock.recvfrom(self._bufsize)
            if data:
                self.push(Read(address, data), "read", self.channel)
            else:
                self.close(self._sock)
        except socket.error, e:
            self.push(Error(self._sock, e), "error", self.channel)
            self._close(self._sock)

    def _write(self, address, data):
        try:
            bytes = self._sock.sendto(data, address)
            if bytes < len(data):
                self._buffers[self._sock].appendleft(data[bytes:])
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

    def broadcast(self, data, port):
        self.write(("<broadcast>", port), data)

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

def Pipe(channels=("pipe.a", "pipe.b"), **kwargs):
    """Create a new full duplex Pipe

    Returns a pair of UNIXClient instances connected on either side of
    the pipe.
    """

    s1, s2 = socket.socketpair()
    a = UNIXClient(s1, channel=channels[0], **kwargs)
    b = UNIXClient(s2, channel=channels[1], **kwargs)
    a._connected = True
    a._poller.addReader(a._sock)
    b._connected = True
    b._poller.addReader(b._sock)
    return a, b
