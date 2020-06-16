"""Socket Components

This module contains various Socket Components for use with Networking.
"""
import os
import select
from collections import defaultdict, deque
from errno import (
    EAGAIN, EALREADY, EBADF, ECONNABORTED, EINPROGRESS, EINTR, EINVAL, EISCONN,
    EMFILE, ENFILE, ENOBUFS, ENOMEM, ENOTCONN, EPERM, EPIPE, EWOULDBLOCK,
)
from socket import (
    AF_INET, AF_INET6, IPPROTO_IP, IPPROTO_TCP, SO_BROADCAST, SO_REUSEADDR,
    SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, TCP_NODELAY, error as SocketError,
    gaierror, getaddrinfo, getfqdn, gethostbyname, gethostname, socket,
)
from time import time

from _socket import socket as SocketType

from circuits.core import BaseComponent, handler
from circuits.core.pollers import BasePoller, Poller
from circuits.core.utils import findcmp
from circuits.six import binary_type

from .events import (
    close, closed, connect, connected, disconnect, disconnected, error, read,
    ready, unreachable, write,
)

try:
    from socket import AF_UNIX
except ImportError:
    AF_UNIX = None


try:
    from ssl import wrap_socket as ssl_socket
    from ssl import CERT_NONE, PROTOCOL_SSLv23
    from ssl import SSLError, SSL_ERROR_WANT_WRITE, SSL_ERROR_WANT_READ

    HAS_SSL = 1
except ImportError:
    import warnings
    warnings.warn("No SSL support available.")
    HAS_SSL = 0
    CERT_NONE = None
    PROTOCOL_SSLv23 = None


BUFSIZE = 4096  # 4KB Buffer
BACKLOG = 5000  # 5K Concurrent Connections


def do_handshake(sock, on_done=None, on_error=None, extra_args=None):
    """SSL Async Handshake

    :param on_done: Function called when handshake is complete
    :type on_done: :function:

    :param on_error: Function called when handshake errored
    :type on_error: :function:
    """

    extra_args = extra_args or ()

    while True:
        try:
            sock.do_handshake()
            break
        except SSLError as err:
            if err.args[0] == SSL_ERROR_WANT_READ:
                select.select([sock], [], [])
            elif err.args[0] == SSL_ERROR_WANT_WRITE:
                select.select([], [sock], [])
            else:
                callable(on_error) and on_error(sock, err)
                return

        yield

    callable(on_done) and on_done(sock, *extra_args)


class Client(BaseComponent):

    channel = "client"

    socket_family = AF_INET
    socket_type = SOCK_STREAM
    socket_protocol = IPPROTO_IP
    socket_options = []

    def __init__(self, bind=None, bufsize=BUFSIZE, channel=channel, **kwargs):
        super(Client, self).__init__(channel=channel, **kwargs)

        if isinstance(bind, SocketType):
            self._bind = bind.getsockname()
            self._sock = bind
        else:
            self._bind = self.parse_bind_parameter(bind)
            self._sock = self._create_socket()

        self._bufsize = bufsize

        self._ssock = None
        self._poller = None
        self._buffer = deque()
        self._closeflag = False
        self._connected = False

        self.host = None
        self.port = 0
        self.secure = False

        self.server = {}
        self.issuer = {}

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv4_parameter(bind_parameter)

    @property
    def connected(self):
        return getattr(self, "_connected", None)

    @handler("registered", "started", channel="*")
    def _on_registered_or_started(self, component, manager=None):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self.fire(ready(self))
            else:
                if component is not self:
                    return
                component = findcmp(self.root, BasePoller)
                if component is not None:
                    self._poller = component
                    self.fire(ready(self))
                else:
                    self._poller = Poller().register(self)
                    self.fire(ready(self))

    @handler("stopped", channel="*")
    def _on_stopped(self, component):
        self.fire(close())

    @handler("read_value_changed")
    def _on_read_value_changed(self, value):
        if isinstance(value, binary_type):
            self.fire(write(value))

    @handler("prepare_unregister", channel="*")
    def _on_prepare_unregister(self, event, c):
        if event.in_subtree(self):
            self._close()

    def _close(self):
        if not self._connected:
            return

        self._poller.discard(self._sock)

        self._buffer.clear()
        self._closeflag = False
        self._connected = False

        try:
            self._sock.shutdown(2)
        except SocketError:
            pass
        try:
            self._sock.close()
        except SocketError:
            pass

        self.fire(disconnected())

    @handler("close")
    def close(self):
        if not self._buffer:
            self._close()
        elif not self._closeflag:
            self._closeflag = True

    def _read(self):
        try:
            try:
                if self.secure and self._ssock:
                    data = self._ssock.read(self._bufsize)
                else:
                    data = self._sock.recv(self._bufsize)
            except SSLError as exc:
                if exc.errno in (SSL_ERROR_WANT_READ, SSL_ERROR_WANT_WRITE):
                    return
                raise

            if data:
                self.fire(read(data)).notify = True
            else:
                self.close()
        except SocketError as e:
            if e.args[0] == EWOULDBLOCK:
                return
            else:
                self.fire(error(e))
                self._close()

    def _write(self, data):
        try:
            if self.secure and self._ssock:
                nbytes = self._ssock.write(data)
            else:
                nbytes = self._sock.send(data)

            if nbytes < len(data):
                self._buffer.appendleft(data[nbytes:])
        except SocketError as e:
            if e.args[0] in (EPIPE, ENOTCONN):
                self._close()
            else:
                self.fire(error(e))

    @handler("write")
    def write(self, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self, self._sock)
        self._buffer.append(data)

    @handler("_disconnect", priority=1)
    def __on_disconnect(self, sock):
        self._close()

    @handler("_read", priority=1)
    def __on_read(self, sock):
        self._read()

    @handler("_write", priority=1)
    def __on_write(self, sock):
        if self._buffer:
            data = self._buffer.popleft()
            self._write(data)

        if not self._buffer:
            if self._closeflag:
                self._close()
            elif self._poller.isWriting(self._sock):
                self._poller.removeWriter(self._sock)

    def _create_socket(self):
        sock = socket(self.socket_family, self.socket_type, self.socket_protocol)

        for option in self.socket_options:
            sock.setsockopt(*option)
        sock.setblocking(False)
        if self._bind is not None:
            sock.bind(self._bind)
        return sock


class TCPClient(Client):

    socket_family = AF_INET
    socket_type = SOCK_STREAM
    socket_protocol = IPPROTO_TCP
    socket_options = [
        (IPPROTO_TCP, TCP_NODELAY, 1),
    ]

    def init(self, connect_timeout=5, *args, **kwargs):
        self.connect_timeout = connect_timeout

    @handler("connect")  # noqa
    def connect(self, host, port, secure=False, **kwargs):
        # XXX: C901: This has a high McCacbe complexity score of 10.
        # TODO: Refactor this!

        self.host = host
        self.port = port
        self.secure = secure

        if self.secure:
            self.certfile = kwargs.get("certfile", None)
            self.keyfile = kwargs.get("keyfile", None)
            self.ca_certs = kwargs.get("ca_certs", None)

        try:
            r = self._sock.connect((host, port))
        except SocketError as e:
            if e.args[0] in (EBADF, EINVAL,):
                self._sock = self._create_socket()
                r = self._sock.connect_ex((host, port))
            else:
                r = e.args[0]

            if r not in (EISCONN, EWOULDBLOCK, EINPROGRESS, EALREADY):
                self.fire(unreachable(host, port, e))
                self.fire(error(e))
                self._close()
                return

        stop_time = time() + self.connect_timeout
        while time() < stop_time:
            try:
                self._sock.getpeername()
                self._connected = True
                break
            except Exception:
                yield

        if not self._connected:
            self.fire(unreachable(host, port))
            return

        def on_done(sock):
            self._poller.addReader(self, sock)
            self.fire(connected(host, port))

        if self.secure:
            def on_error(sock, err):
                self.fire(error(sock, err))
                self._close()

            self._sock = ssl_socket(
                self._sock, self.keyfile, self.certfile, ca_certs=self.ca_certs,
                do_handshake_on_connect=False
            )
            for _ in do_handshake(self._sock, on_done, on_error):
                yield
        else:
            on_done(self._sock)


class TCP6Client(TCPClient):

    socket_family = AF_INET6

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv6_parameter(bind_parameter)


class UNIXClient(Client):

    socket_family = AF_UNIX
    socket_type = SOCK_STREAM
    socket_options = []

    @handler("ready")
    def ready(self, component):
        if self._poller is not None and self._connected:
            self._poller.addReader(self, self._sock)

    @handler("connect")  # noqa
    def connect(self, path, secure=False, **kwargs):
        # XXX: C901: This has a high McCacbe complexity score of 10.
        # TODO: Refactor this!

        self.path = path
        self.secure = secure

        if self.secure:
            self.certfile = kwargs.get("certfile", None)
            self.keyfile = kwargs.get("keyfile", None)
            self.ca_certs = kwargs.get("ca_certs", None)

        try:
            r = self._sock.connect_ex(path)
        except SocketError as e:
            r = e.args[0]

        if r:
            if r in (EISCONN, EWOULDBLOCK, EINPROGRESS, EALREADY):
                self._connected = True
            else:
                self.fire(error(r))
                return

        self._connected = True

        self._poller.addReader(self, self._sock)

        if self.secure:
            def on_done(sock):
                self.fire(connected(gethostname(), path))

            def on_error(sock, err):
                self.fire(error(err))

            self._ssock = ssl_socket(
                self._sock, self.keyfile, self.certfile, ca_certs=self.ca_certs,
                do_handshake_on_connect=False
            )
            for _ in do_handshake(self._ssock, on_done, on_error):
                yield
        else:
            self.fire(connected(gethostname(), path))


class Server(BaseComponent):

    channel = "server"
    socket_protocol = IPPROTO_IP

    def __init__(self, bind, secure=False, backlog=BACKLOG,
                 bufsize=BUFSIZE, channel=channel, **kwargs):
        super(Server, self).__init__(channel=channel)

        self.socket_options = self.socket_options[:] + kwargs.get('socket_options', [])
        self._bind = self.parse_bind_parameter(bind)

        self._backlog = backlog
        self._bufsize = bufsize

        if isinstance(bind, socket):
            self._sock = bind
        else:
            self._sock = self._create_socket()

        self._closeq = []
        self._clients = []
        self._poller = None
        self._buffers = defaultdict(deque)

        self.__starttls = set()

        self.secure = secure
        self.certfile = kwargs.get("certfile")
        self.keyfile = kwargs.get("keyfile", None)
        self.cert_reqs = kwargs.get("cert_reqs", CERT_NONE)
        self.ssl_version = kwargs.get("ssl_version", PROTOCOL_SSLv23)
        self.ca_certs = kwargs.get("ca_certs", None)
        if self.secure and not self.certfile:
            raise RuntimeError("certfile must be specified for server-side operations")

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv4_parameter(bind_parameter)

    @property
    def connected(self):
        return True

    @property
    def host(self):
        if getattr(self, "_sock", None) is not None:
            try:
                sockname = self._sock.getsockname()
                if isinstance(sockname, tuple):
                    return sockname[0]
                else:
                    return sockname
            except SocketError:
                return None

    @property
    def port(self):
        if getattr(self, "_sock", None) is not None:
            try:
                sockname = self._sock.getsockname()
                if isinstance(sockname, tuple):
                    return sockname[1]
            except SocketError:
                return None

    @handler("registered", "started", channel="*")
    def _on_registered_or_started(self, component, manager=None):
        if self._poller is None:
            if isinstance(component, BasePoller):
                self._poller = component
                self._poller.addReader(self, self._sock)
                self.fire(ready(self, (self.host, self.port)))
            else:
                if component is not self:
                    return
                component = findcmp(self.root, BasePoller)
                if component is not None:
                    self._poller = component
                    self._poller.addReader(self, self._sock)
                    self.fire(ready(self, (self.host, self.port)))
                else:
                    self._poller = Poller().register(self)
                    self._poller.addReader(self, self._sock)
                    self.fire(ready(self, (self.host, self.port)))

    @handler("stopped", channel="*")
    def _on_stopped(self, component):
        self.fire(close())

    @handler("read_value_changed")
    def _on_read_value_changed(self, value):
        if isinstance(value.value, binary_type):
            sock = value.event.args[0]
            self.fire(write(sock, value.value))

    def _close(self, sock):
        if sock is None:
            return

        if sock != self._sock and sock not in self._clients:
            return

        self._poller.discard(sock)

        if sock in self._buffers:
            del self._buffers[sock]

        if sock in self._clients:
            self._clients.remove(sock)
        else:
            self._sock = None

        if sock in self.__starttls:
            self.__starttls.remove(sock)

        try:
            sock.shutdown(2)
        except SocketError:
            pass
        try:
            sock.close()
        except SocketError:
            pass

        self.fire(disconnect(sock))

    @handler("close")
    def close(self, sock=None):
        is_closed = sock is None

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

        if is_closed:
            self.fire(closed())

    def _read(self, sock):
        if sock not in self._clients:
            return

        try:
            data = sock.recv(self._bufsize)
            if data:
                self.fire(read(sock, data)).notify = True
            else:
                self.close(sock)
        except SocketError as e:
            if e.args[0] == EWOULDBLOCK:
                return
            else:
                self.fire(error(sock, e))
                self._close(sock)

    def _write(self, sock, data):
        if sock not in self._clients:
            return

        try:
            nbytes = sock.send(data)
            if nbytes < len(data):
                self._buffers[sock].appendleft(data[nbytes:])
        except SocketError as e:
            if e.args[0] not in (EINTR, EWOULDBLOCK, ENOBUFS):
                self.fire(error(sock, e))
                self._close(sock)
            else:
                self._buffers[sock].appendleft(data)

    @handler("write")
    def write(self, sock, data):
        if not self._poller.isWriting(sock):
            self._poller.addWriter(self, sock)
        self._buffers[sock].append(data)

    def _accept(self):
        try:
            newsock, host = self._sock.accept()
        except SocketError as e:
            if e.args[0] in (EWOULDBLOCK, EAGAIN):
                return
            elif e.args[0] == EPERM:
                # Netfilter on Linux may have rejected the
                # connection, but we get told to try to accept()
                # anyway.
                return
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
                return
            else:
                raise

        if self.secure and HAS_SSL:
            for _ in self._do_handshake(newsock):
                yield
        else:
            self._on_accept_done(newsock)

    def _do_handshake(self, sock, fire_connect_event=True):
        sslsock = ssl_socket(
            sock,
            server_side=True,
            keyfile=self.keyfile,
            ca_certs=self.ca_certs,
            certfile=self.certfile,
            cert_reqs=self.cert_reqs,
            ssl_version=self.ssl_version,
            do_handshake_on_connect=False
        )

        for _ in do_handshake(sslsock, self._on_accept_done, self._on_handshake_error, (fire_connect_event,)):
            yield _

    def _on_accept_done(self, sock, fire_connect_event=True):
        sock.setblocking(False)
        self._poller.addReader(self, sock)
        self._clients.append(sock)
        if fire_connect_event:
            try:
                self.fire(connect(sock, *sock.getpeername()))
            except SocketError as exc:
                # errno 107 (ENOTCONN): the client already disconnected
                self._on_handshake_error(sock, exc)

    def _on_handshake_error(self, sock, err):
        self.fire(error(sock, err))
        self._close(sock)

    @handler('starttls')
    def starttls(self, sock):
        if not HAS_SSL:
            raise RuntimeError('Cannot start TLS. No TLS support.')
        if sock in self.__starttls:
            raise RuntimeError('Cannot reuse socket for already started STARTTLS.')
        self.__starttls.add(sock)
        self._poller.removeReader(sock)
        self._clients.remove(sock)
        for _ in self._do_handshake(sock, False):
            yield

    @handler("_disconnect", priority=1)
    def _on_disconnect(self, sock):
        self._close(sock)

    @handler("_read", priority=1)
    def _on_read(self, sock):
        if sock == self._sock:
            return self._accept()
        else:
            self._read(sock)

    @handler("_write", priority=1)
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

    def _create_socket(self):
        sock = socket(self.socket_family, self.socket_type, self.socket_protocol)

        for option in self.socket_options:
            sock.setsockopt(*option)
        sock.setblocking(False)
        if self._bind is not None:
            sock.bind(self._bind)
        return sock


class TCPServer(Server):

    socket_family = AF_INET
    socket_type = SOCK_STREAM
    socket_options = [
        (SOL_SOCKET, SO_REUSEADDR, 1),
        (IPPROTO_TCP, TCP_NODELAY, 1),
    ]

    def _create_socket(self):
        sock = super(TCPServer, self)._create_socket()
        sock.listen(self._backlog)

        return sock

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv4_parameter(bind_parameter)


def parse_ipv4_parameter(bind_parameter):
    if isinstance(bind_parameter, int):
        try:
            bind = (gethostbyname(gethostname()), bind_parameter)
        except gaierror:
            bind = ("0.0.0.0", bind_parameter)
    elif isinstance(bind_parameter, str) and ":" in bind_parameter:
        host, port = bind_parameter.split(":")
        port = int(port)
        bind = (host, port)
    else:
        bind = bind_parameter

    return bind


def parse_ipv6_parameter(bind_parameter):
    if isinstance(bind_parameter, int):
        try:
            _, _, _, _, bind \
                = getaddrinfo(getfqdn(), bind_parameter, AF_INET6)[0]
        except (gaierror, IndexError):
            bind = ("::", bind_parameter)
    else:
        bind = bind_parameter

    return bind


class TCP6Server(TCPServer):

    socket_family = AF_INET6

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv6_parameter(bind_parameter)


class UNIXServer(Server):

    socket_family = AF_UNIX
    socket_type = SOCK_STREAM
    socket_options = [
        (SOL_SOCKET, SO_REUSEADDR, 1),
    ]

    def _create_socket(self):
        if os.path.exists(self._bind):
            os.unlink(self._bind)

        sock = super(UNIXServer, self)._create_socket()
        sock.listen(self._backlog)

        return sock


class UDPServer(Server):

    socket_family = AF_INET
    socket_type = SOCK_DGRAM
    socket_options = [
        (SOL_SOCKET, SO_BROADCAST, 1),
        (SOL_SOCKET, SO_REUSEADDR, 1)
    ]

    def _close(self, sock):
        self._poller.discard(sock)

        if sock in self._buffers:
            del self._buffers[sock]

        try:
            sock.shutdown(2)
        except SocketError:
            pass
        try:
            sock.close()
        except SocketError:
            pass

        self.fire(disconnect(sock))

    @handler("close", override=True)
    def close(self):
        self.fire(closed())

        if self._buffers[self._sock] and self._sock not in self._closeq:
            self._closeq.append(self._sock)
        else:
            self._close(self._sock)

    def _read(self):
        try:
            data, address = self._sock.recvfrom(self._bufsize)
            if data:
                self.fire(read(address, data)).notify = True
        except SocketError as e:
            if e.args[0] in (EWOULDBLOCK, EAGAIN):
                return
            self.fire(error(self._sock, e))
            self._close(self._sock)

    def _write(self, address, data):
        try:
            bytes = self._sock.sendto(data, address)
            if bytes < len(data):
                self._buffers[self._sock].appendleft(data[bytes:])
        except SocketError as e:
            if e.args[0] in (EPIPE, ENOTCONN):
                self._close(self._sock)
            else:
                self.fire(error(self._sock, e))

    @handler("write", override=True)
    def write(self, address, data):
        if not self._poller.isWriting(self._sock):
            self._poller.addWriter(self, self._sock)
        self._buffers[self._sock].append((address, data))

    @handler("broadcast", override=True)
    def broadcast(self, data, port):
        self.write(("<broadcast>", port), data)

    @handler("_disconnect", priority=1, override=True)
    def _on_disconnect(self, sock):
        self._close(sock)

    @handler("_read", priority=1, override=True)
    def _on_read(self, sock):
        self._read()

    @handler("_write", priority=1, override=True)
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


class UDP6Server(UDPServer):
    socket_family = AF_INET6

    def parse_bind_parameter(self, bind_parameter):
        return parse_ipv6_parameter(bind_parameter)


UDP6Client = UDP6Server


def Pipe(*channels, **kwargs):
    """Create a new full duplex Pipe

    Returns a pair of UNIXClient instances connected on either side of
    the pipe.
    """

    from socket import socketpair

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
