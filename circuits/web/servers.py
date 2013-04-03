# Module:   server
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Web Servers

This module implements the several Web Server components.
"""


from circuits import io
from circuits.tools import deprecated
from circuits.net.sockets import Read, Write
from circuits.core import handler, BaseComponent
from circuits.net.sockets import TCPServer, UNIXServer

from .http import HTTP
from .events import WebEvent
from .dispatchers import Dispatcher


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
                 channel=channel):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(BaseServer, self).__init__(channel=channel)

        if any((isinstance(bind, o) for o in (int, list, tuple,))):
            SocketType = TCPServer
        else:
            SocketType = TCPServer if ":" in bind else UNIXServer

        self.server = SocketType(
            bind,
            secure=secure,
            certfile=certfile,
            channel=channel
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
    def secure(self):
        if hasattr(self, "server"):
            return self.server.secure

    @property
    @deprecated
    def base(self):
        """
        .. deprecated:: 2.2
           Use :attr:~.http.base`
        """

        if hasattr(self, "http"):
            return self.http.base

    @property
    @deprecated
    def scheme(self):
        """
        .. deprecated:: 2.2
           Use :attr:~.http.scheme`
        """

        if hasattr(self, "http"):
            return self.http.scheme

    @property
    @deprecated
    def protocol(self):
        """
        .. deprecated:: 2.2
           Use :attr:~.http.protocol`
        """

        if hasattr(self, "http"):
            return self.http.protocol

    @deprecated
    def version(self):
        """
        .. deprecated:: 2.2
           Use :attr:~.http.version`
        """

        if hasattr(self, "http"):
            return self.http.version

    @handler("ready")
    def _on_ready(self, server, bind):
        print(
            "{0:s} ready! Listening on: {1:s}".format(
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

        Dispatcher(channel=self.channel).register(self)


class FakeSock():
    def getpeername(self):
        return (None, None)


class StdinServer(BaseComponent):

    channel = "web"

    def __init__(self, encoding="utf-8", channel=channel):
        super(StdinServer, self).__init__(channel=channel)

        WebEvent.channels = (channel,)

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
        self.fire(Read(FakeSock(), data))

    @handler("write")
    def write(self, sock, data):
        self.fire(Write(data))
