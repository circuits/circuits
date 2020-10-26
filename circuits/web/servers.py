"""Web Servers

This module implements the several Web Server components.
"""
from sys import stderr

from circuits import io
from circuits.core import BaseComponent, Timer, handler
from circuits.net.events import close, read, write
from circuits.net.sockets import BUFSIZE, TCPServer, UNIXServer

from .dispatchers import Dispatcher
from .events import terminate
from .http import HTTP


class BaseServer(BaseComponent):

    """Create a Base Web Server

    Create a Base Web Server (HTTP) bound to the IP Address / Port or
    UNIX Socket specified by the 'bind' parameter.

    :ivar server: Reference to underlying Server Component

    :param bind: IP Address / Port or UNIX Socket to bind to.
    :type bind: Instance of int, list, tuple or str

    The 'bind' parameter is quite flexible with what valid values it accepts.

    If an int is passed, a TCPServer will be created. The Server will be
    bound to the Port given by the 'bind' argument and the bound interface
    will default (normally to  "0.0.0.0").

    If a list or tuple is passed, a TCPServer will be created. The
    Server will be bound to the Port given by the 2nd item in the 'bind'
    argument and the bound interface will be the 1st item.

    If a str is passed and it contains the ':' character, this is
    assumed to be a request to bind to an IP Address / Port. A TCpServer
    will thus be created and the IP Address and Port will be determined
    by splitting the string given by the 'bind' argument.

    Otherwise if a str is passed and it does not contain the ':'
    character, a file path is assumed and a UNIXServer is created and
    bound to the file given by the 'bind' argument.
    """

    channel = "web"

    def __init__(self, bind, encoding="utf-8", secure=False, certfile=None,
                 channel=channel, display_banner=True, bufsize=BUFSIZE):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(BaseServer, self).__init__(channel=channel)

        self._display_banner = display_banner

        if isinstance(bind, (int, list, tuple,)):
            SocketType = TCPServer
        else:
            SocketType = TCPServer if ":" in bind else UNIXServer

        self.server = SocketType(
            bind,
            secure=secure,
            certfile=certfile,
            channel=channel,
            bufsize=bufsize
        ).register(self)

        self.http = HTTP(
            self, encoding=encoding, channel=channel
        ).register(self)

    @property
    def host(self):
        if hasattr(self, "server"):
            return self.server.host

    @property
    def port(self):
        if hasattr(self, "server"):
            return self.server.port

    @property
    def display_banner(self):
        return getattr(self, "_display_banner", False)

    @property
    def secure(self):
        if hasattr(self, "server"):
            return self.server.secure

    @handler("connect")
    def _on_connect(self, *args, **kwargs):
        """Dummy Event Handler for connect"""

    @handler("closed")
    def _on_closed(self, *args, **kwargs):
        """Dummy Event Handler for closed"""

    @handler("signal")
    def _on_signal(self, *args, **kwargs):
        """signal Event Handler"""

        self.fire(close())
        Timer(3, terminate()).register(self)

    @handler("terminate")
    def _on_terminate(self):
        raise SystemExit(0)

    @handler("ready")
    def _on_ready(self, server, bind):
        stderr.write(
            "{0:s} ready! Listening on: {1:s}\n".format(
                self.http.version, self.http.base
            )
        )


class Server(BaseServer):

    """Create a Web Server

    Create a Web Server (HTTP) complete with the default Dispatcher to
    parse requests and posted form data dispatching to appropriate
    Controller(s).

    See: circuits.web.servers.BaseServer
    """

    def __init__(self, bind, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Server, self).__init__(bind, **kwargs)

        Dispatcher(channel=self.channel).register(self.http)


class FakeSock():

    def getpeername(self):
        return (None, None)


class StdinServer(BaseComponent):

    channel = "web"

    def __init__(self, encoding="utf-8", channel=channel):
        super(StdinServer, self).__init__(channel=channel)

        self.server = (io.stdin + io.stdout).register(self)
        self.http = HTTP(
            self, encoding=encoding, channel=channel
        ).register(self)

        Dispatcher(channel=self.channel).register(self)

    @property
    def host(self):
        return io.stdin.filename

    @property
    def port(self):
        return 0

    @property
    def secure(self):
        return False

    @handler("read", channel="stdin")
    def read(self, data):
        self.fire(read(FakeSock(), data))

    @handler("write")
    def write(self, sock, data):
        self.fire(write(data))
