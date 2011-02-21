# Module:   sockets
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Socket Components

This module contains various Socket Components for use with Networking.
"""

import os
from collections import defaultdict, deque

from errno import EAGAIN, EALREADY, EBADF
from errno import ECONNABORTED, EINPROGRESS, EISCONN, EMFILE, ENFILE
from errno import ENOBUFS, ENOMEM, ENOTCONN, EPERM, EPIPE, EINVAL, EWOULDBLOCK

from _socket import socket as SocketType

from socket import gaierror, error as SocketError
from socket import gethostname, gethostbyname, socket, socketpair

from socket import SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, TCP_NODELAY
from socket import AF_INET, AF_UNIX, IPPROTO_TCP, SOCK_STREAM, SOCK_DGRAM

try:
    from ssl import wrap_socket as ssl_socket
    from ssl import CERT_NONE, PROTOCOL_SSLv23, SSLError
    HAS_SSL = 1
except ImportError:
    import warnings
    warnings.warn("No SSL support available.")
    HAS_SSL = 0

from circuits.core.utils import findcmp
from circuits.core import handler, Event, Component
from circuits.core.pollers import BasePoller, Poller

BUFSIZE = 4096 # 4KB Buffer
BACKLOG = 5000 #  5K Concurrent Connections

###
### Event Objects
###

class Connect(Event):
    """Connect Event

    This Event is sent when a new client connection has arrived on a server.
    This event is also used for client's to initiate a new connection to
    a remote host.

    @note: This event is used for both Client and Server Components.

    :param args:  Client: (host, port) Server: (sock, host, port)
    :type  args: tuple

    :param kwargs: Client: (ssl)
    :type  kwargs: dict
    """

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Connect, self).__init__(*args, **kwargs)

class Disconnect(Event):
    """Disconnect Event

    This Event is sent when a client connection has closed on a server.
    This event is also used for client's to disconnect from a remote host.

    @note: This event is used for both Client and Server Components.

    :param args:  Client: () Server: (sock)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Disconnect, self).__init__(*args)

class Connected(Event):
    """Connected Event

    This Event is sent when a client has successfully connected.

    @note: This event is for Client Components.

    :param host: The hostname connected to.
    :type  str:  str

    :param port: The port connected to
    :type  int:  int
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

    :param args:  Client: (data) Server: (sock, data)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Read, self).__init__(*args)

class Error(Event):
    """Error Event

    This Event is sent when a client or server connection has an error.

    @note: This event is used for both Client and Server Components.

    :param args:  Client: (error) Server: (sock, error)
    :type  tuple: tuple
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

    :param args:  Client: (data) Server: (sock, data)
    :type  tuple: tuple
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

    :param args:  Client: () Server: (sock)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Close, self).__init__(*args)

class Ready(Event):
    """Ready Event

    This Event is used to notify the rest of the system that the underlying
    Client or Server Component is ready to begin processing connections or
    incoming/outgoing data. (This is triggered as a direct result of having
    the capability to support multiple client/server components with a snigle
    poller component instnace in a system).

    @note: This event is used for both Client and Server Components.

    :param component:  The Client/Server Component that is ready.
    :type  tuple: Component (Client/Server)
    """

    def __init__(self, component):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Ready, self).__init__(component)

class Closed(Event):
    """Closed Event

    This Event is sent when a server has closed it's listening socket.

    @note: This event is for Server components.
    """

    def __init__(self):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Closed, self).__init__()

###
### Components
###

class Client(Component):

    channel = "client"

    def __init__(self, bind=None, **kwargs):
        channel = kwargs.get("channel", self.__class__.channel)
        super(Client, self).__init__(channel=channel)

        self.encoding = kwargs.get("encoding", "utf-8")

        if type(bind) is int:
            try:
                self.bind = (gethostbyname(gethostname()), bind)
            except gaierror:
                self.bind = ("0.0.0.0", bind)
        elif type(bind) is str and ":" in bind:
            host, port = bind.split(":")
            port = int(port)
            self.bind = (host, port)
        else:
            self.bind = bind

        self.host = "0.0.0.0"
        self.port = 0
        self.secure  = False

        self.server = {}
        self.issuer = {}

        self._bufsize = kwargs.get("bufsize", BUFSIZE)

        self._poller = None

        self._sock = None
        self._ssock = None
        self._buffer = deque()
        self._closeflag = False
        self._connected = False

    @property
    def connected(self):
        return getattr(self, "_connected", None)

    @handler("registered", target="*")
    def _on_registered(self, component, manager):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self.push(Ready(self), "ready", self.channel)
            else:
                component = findcmp(self.root, BasePoller, subclass=False)
                if component is not None:
                    self._poller = component
                    self.push(Ready(self), "ready", self.channel)
                else:
                    self._poller = Poller().register(self)
                    self.push(Ready(self), "ready", self.channel)

    @handler("started", filter=True, target="*")
    def _on_started(self, component, mode):
        if self._poller is None:
            self._poller = Poller().register(self)
            self.push(Ready(self), "ready", self.channel)
            return True

    @handler("stopped", target="*")
    def _on_stopped(self, component):
        self.push(Close(), "close", self.channel)

    def _close(self):
        self._poller.discard(self._sock)

        self._buffer.clear()
        self._closeflag = False
        self._connected = False

        try:
            self._sock.shutdown(2)
            self._sock.close()
        except SocketError:
            pass

        self.push(Disconnected(), "disconnected", self.channel)

    def close(self):
        if not self._buffer:
            self._close()
        elif not self._closeflag:
            self._closeflag = True

    def _read(self):
        try:
            if self.secure and self._ssock:
                data = self._ssock.read(self._bufsize)
            else:
                data = self._sock.recv(self._bufsize)

            if data:
                self.push(Read(data), "read", self.channel)
            else:
                self.close()
        except SocketError, e:
            if e[0] == EWOULDBLOCK:
                return
            else:
                self.push(Error(e), "error", self.channel)
                self._close()

    def _write(self, data):
        try:
            if type(data) is unicode:
                data = data.encode(self.encoding)

            if self.secure and self._ssock:
                bytes = self._ssock.write(data)
            else:
                bytes = self._sock.send(data)

            if bytes < len(data):
                self._buffer.appendleft(data[bytes:])
        except SocketError, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close()
            else:
                self.push(Error(e), "error", self.channel)

    def write(self, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self, self._sock)
        self._buffer.append(data)

    @handler("_disconnect", filter=True)
    def __on_disconnect(self, sock):
        self._close()

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
            self._sock = self._create_socket()

    def _create_socket(self):
        sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        if self.bind is not None:
            sock.bind((self.bind, 0))

        sock.setblocking(False)
        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)

        return sock

    def connect(self, host, port, secure=False, **kwargs):
        self.host = host
        self.port = port
        self.secure  = secure

        if self.secure:
            self.certfile = kwargs.get("certfile", None)
            self.keyfile = kwargs.get("keyfile", None)

        try:
            r = self._sock.connect_ex((host, port))
        except SocketError, e:
            if e[0] in (EBADF, EINVAL,):
                self._sock = self._create_socket()
                r = self._sock.connect_ex((host, port))
            else:
                r = e[0]

        if r:
            if r in (EISCONN, EWOULDBLOCK, EINPROGRESS, EALREADY):
                self._connected = True
            else:
                self.push(Error(r), "error", self.channel)
                return

        self._connected = True

        self._poller.addReader(self, self._sock)

        if self.secure:
            self._ssock = ssl_socket(self._sock, self.keyfile, self.certfile)

        self.push(Connected(host, port), "connected", self.channel)

class UNIXClient(Client):

    def __init__(self, bind=None, **kwargs):
        super(UNIXClient, self).__init__(bind, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = self._create_socket()

    def _create_socket(self):
        sock = socket(AF_UNIX, SOCK_STREAM)
        if self.bind is not None:
            sock.bind(self.bind)

        sock.setblocking(False)

        return sock

    @handler("registered", target="*")
    def _on_registered(self, component, manager):
        if self._poller is not None and self._connected:
            self._poller.addReader(self, self._sock)

    def connect(self, path, secure=False, **kwargs):
        self.path = path
        self.secure = secure

        if self.secure:
            self.certfile = kwargs.get("certfile", None)
            self.keyfile = kwargs.get("keyfile", None)

        try:
            r = self._sock.connect_ex(path)
        except SocketError, e:
            r = e[0]

        if r:
            if r in (EISCONN, EWOULDBLOCK, EINPROGRESS, EALREADY):
                self._connected = True
            else:
                self.push(Error(r), "error", self.channel)
                return

        self._connected = True

        self._poller.addReader(self, self._sock)

        if self.secure:
            self._ssock = ssl_socket(self._sock, self.keyfile, self.certfile)

        self.push(Connected(gethostname(), path), "connected", self.channel)


class Server(Component):

    channel = "server"

    def __init__(self, bind, secure=False, **kwargs):
        channel = kwargs.get("channel", self.__class__.channel)
        super(Server, self).__init__(channel=channel)

        self.encoding = kwargs.get("encoding", "utf-8")

        if type(bind) is int:
            try:
                self.bind = (gethostbyname(gethostname()), bind)
            except gaierror:
                self.bind = ("0.0.0.0", bind)
        elif type(bind) is str and ":" in bind:
            host, port = bind.split(":")
            port = int(port)
            self.bind = (host, port)
        else:
            self.bind = bind

        self.secure = secure

        if self.secure:
            self.certfile = kwargs.get("certfile", None)
            self.keyfile = kwargs.get("keyfile", None)
            self.cert_reqs = kwargs.get("cert_reqs", CERT_NONE)
            self.ssl_version = kwargs.get("ssl_version", PROTOCOL_SSLv23)
            self.ca_certs = kwargs.get("ca_certs", None)

        self._bufsize = kwargs.get("bufsize", BUFSIZE)
        self._backlog = kwargs.get("backlog", BACKLOG)

        self._poller = None

        self._sock = None
        self._buffers = defaultdict(deque)
        self._closeq = []
        self._clients = []

    @property
    def connected(self):
        return True

    @property
    def host(self):
        if hasattr(self, "_sock"):
            return self._sock.getsockname()[0]

    @property
    def port(self):
        if hasattr(self, "_sock"):
            return self._sock.getsockname()[1]

    @handler("registered", target="*")
    def _on_registered(self, component, manager):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self._poller.addReader(self, self._sock)
                self.push(Ready(self), "ready", self.channel)
            else:
                component = findcmp(self.root, BasePoller, subclass=False)
                if component is not None:
                    self._poller = component
                    self._poller.addReader(self, self._sock)
                    self.push(Ready(self), "ready", self.channel)
                else:
                    self._poller = Poller().register(self)
                    self._poller.addReader(self, self._sock)
                    self.push(Ready(self), "ready", self.channel)

    @handler("started", filter=True, target="*")
    def _on_started(self, component, mode):
        if self._poller is None:
            self._poller = Poller().register(self)
            self._poller.addReader(self, self._sock)
            self.push(Ready(self), "ready", self.channel)
            return True

    @handler("stopped", target="*")
    def _on_stopped(self, component):
        self.push(Close(), "close", self.channel)

    def _close(self, sock):
        if not sock == self._sock and sock not in self._clients:
            return

        self._poller.discard(sock)

        if sock in self._buffers:
            del self._buffers[sock]

        if sock in self._clients:
            self._clients.remove(sock)

        try:
            sock.shutdown(2)
            sock.close()
        except SocketError:
            pass

        self.push(Disconnect(sock), "disconnect", self.channel)

    def close(self, sock=None):
        closed = sock is None

        if sock is None:
            socks = [self._sock]
            socks.extend(self._clients[:])
        else:
            socks = [sock]

        for sock in socks:
            if not self._buffers[sock]:
                self._close(sock)
            elif sock not in self._closeq:
                self._closeq.append(sock)

        if closed:
            self.push(Closed(), "closed", self.channel)

    def _read(self, sock):
        if sock not in self._clients:
            return

        try:
            data = sock.recv(self._bufsize)
            if data:
                self.push(Read(sock, data), "read", self.channel)
            else:
                self.close(sock)
        except SocketError, e:
            if e[0] == EWOULDBLOCK:
                return
            else:
                self.push(Error(sock, e), "error", self.channel)
                self._close(sock)

    def _write(self, sock, data):
        if sock not in self._clients:
            return

        try:
            if type(data) is unicode:
                data = data.encode(self.encoding)

            bytes = sock.send(data)
            if bytes < len(data):
                self._buffers[sock].appendleft(data[bytes:])
        except SocketError, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close(sock)
            else:
                self.push(Error(sock, e), "error", self.channel)

    def write(self, sock, data):
        if not self._poller.isWriting(sock):
            self._poller.addWriter(self, sock)
        self._buffers[sock].append(data)

    def broadcast(self, data):
        for sock in self._clients:
            self.write(sock, data)

    def _accept(self):
        try:
            newsock, host = self._sock.accept()
            if self.secure and HAS_SSL:
                newsock = ssl_socket(newsock,
                    server_side=True,
                    certfile=self.certfile,
                    keyfile=self.keyfile,
                    cert_reqs=self.cert_reqs,
                    ssl_version=self.ssl_version,
                    ca_certs=self.ca_certs)

        except SSLError, e:
            raise

        except SocketError, e:
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
        self._poller.addReader(self, newsock)
        self._clients.append(newsock)
        self.push(Connect(newsock, *host), "connect", self.channel)

    @handler("_disconnect", filter=True)
    def _on_disconnect(self, sock):
        self._close(sock)

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

    def __init__(self, bind, secure=False, **kwargs):
        super(TCPServer, self).__init__(bind, secure, **kwargs)

        if type(bind) is SocketType:
            self.bind = None
            self._sock = bind
        else:
            self._sock = self._create_socket()

    def _create_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)

        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sock.setblocking(False)
        sock.bind(self.bind)
        sock.listen(self._backlog)

        return sock

class UNIXServer(Server):

    def __init__(self, bind, secure=False, **kwargs):
        super(UNIXServer, self).__init__(bind, secure, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = self._create_socket()

    def _create_socket(self):
        if os.path.exists(self.bind):
            os.unlink(self.bind)

        sock = socket(AF_UNIX, SOCK_STREAM)
        sock.bind(self.bind)

        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.listen(self._backlog)

        return sock

    @property
    def host(self):
        if hasattr(self, "bind"):
            return self.bind

class UDPServer(Server):

    def __init__(self, bind, secure=False, **kwargs):
        super(UDPServer, self).__init__(bind, secure, **kwargs)

        if type(bind) is SocketType:
            self._sock = bind
        else:
            self._sock = self._create_socket()

    def _create_socket(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(self.bind)

        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.setblocking(False)

        return sock

    def _close(self, sock):
        self._poller.discard(sock)

        if sock in self._buffers:
            del self._buffers[sock]

        try:
            sock.shutdown(2)
            sock.close()
        except SocketError:
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
        except SocketError, e:
            if e[0] in (EWOULDBLOCK, EAGAIN):
                return
            self.push(Error(self._sock, e), "error", self.channel)
            self._close(self._sock)

    def _write(self, address, data):
        try:
            if type(data) is unicode:
                data = data.encode(self.encoding)

            bytes = self._sock.sendto(data, address)
            if bytes < len(data):
                self._buffers[self._sock].appendleft(data[bytes:])
        except SocketError, e:
            if e[0] in (EPIPE, ENOTCONN):
                self._close(self._sock)
            else:
                self.push(Error(self._sock, e), "error", self.channel)

    @handler("write", override=True)
    def write(self, address, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self, self._sock)
        self._buffers[self._sock].append((address, data))

    def broadcast(self, data, port):
        self.write(("<broadcast>", port), data)

    @handler("_disconnect", filter=True, override=True)
    def _on_disconnect(self, sock):
        self._close(sock)

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

def Pipe(*channels, **kwargs):
    """Create a new full duplex Pipe

    Returns a pair of UNIXClient instances connected on either side of
    the pipe.
    """

    if not channels:
        channels = ("a", "b")

    s1, s2 = socketpair()
    s1.setblocking(False)
    s2.setblocking(False)

    a = UNIXClient(s1, channel=channels[0], **kwargs)
    b = UNIXClient(s2, channel=channels[1], **kwargs)

    a._connected = True
    b._connected = True

    return a, b
