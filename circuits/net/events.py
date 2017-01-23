"""Networking Events

This module implements commonly used Networking events used by socket components.
"""
from circuits.core import Event


class connect(Event):

    """connect Event

    This Event is sent when a new client connection has arrived on a server.
    This event is also used for client's to initiate a new connection to
    a remote host.

    .. note ::
        This event is used for both Client and Server Components.

    :param args:  Client: (host, port) Server: (sock, host, port)
    :type  args: tuple

    :param kwargs: Client: (ssl)
    :type  kwargs: dict
    """

    def __init__(self, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(connect, self).__init__(*args, **kwargs)


class disconnect(Event):

    """disconnect Event

    This Event is sent when a client connection has closed on a server.
    This event is also used for client's to disconnect from a remote host.

    .. note::
        This event is used for both Client and Server Components.

    :param args:  Client: () Server: (sock)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(disconnect, self).__init__(*args)


class connected(Event):

    """connected Event

    This Event is sent when a client has successfully connected.

    .. note::
        This event is for Client Components.

    :param host: The hostname connected to.
    :type  str:  str

    :param port: The port connected to
    :type  int:  int
    """

    def __init__(self, host, port):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(connected, self).__init__(host, port)


class disconnected(Event):

    """disconnected Event

    This Event is sent when a client has disconnected

    .. note::
        This event is for Client Components.
    """

    def __init__(self):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(disconnected, self).__init__()


class read(Event):

    """read Event

    This Event is sent when a client or server connection has read any data.

    .. note::
        This event is used for both Client and Server Components.

    :param args:  Client: (data) Server: (sock, data)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(read, self).__init__(*args)


class error(Event):

    """error Event

    This Event is sent when a client or server connection has an error.

    .. note::
        This event is used for both Client and Server Components.

    :param args:  Client: (error) Server: (sock, error)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(error, self).__init__(*args)


class unreachable(Event):

    """unreachable Event

    This Event is sent when a server is unreachable for a client

    :param host: Server hostname or IP
    :type str: str

    :param port: Server port
    :type int: int
    """

    def __init__(self, host, port, reason=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(unreachable, self).__init__(host, port, reason)


class broadcast(Event):

    """broadcast Event

    This Event is used by the UDPServer/UDPClient sockets to send a message on the ``<broadcast>``
    network.

    .. note::
        - This event is never sent, it is used to send data.
        - This event is used for both Client and Server UDP Components.

    :param args:  (data, port)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(broadcast, self).__init__(*args)


class write(Event):

    """write Event

    This Event is used to notify a client, client connection or server that
    we have data to be written.

    .. note::
        - This event is never sent, it is used to send data.
        - This event is used for both Client and Server Components.

    :param args:  Client: (data) Server: (sock, data)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(write, self).__init__(*args)


class close(Event):

    """close Event

    This Event is used to notify a client, client connection or server that
    we want to close.

    .. note::
        - This event is never sent, it is used to close.
        - This event is used for both Client and Server Components.

    :param args:  Client: () Server: (sock)
    :type  tuple: tuple
    """

    def __init__(self, *args):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(close, self).__init__(*args)


class ready(Event):

    """ready Event

    This Event is used to notify the rest of the system that the underlying
    Client or Server Component is ready to begin processing connections or
    incoming/outgoing data. (This is triggered as a direct result of having
    the capability to support multiple client/server components with a single
    poller component instance in a system).

    .. note::
        This event is used for both Client and Server Components.

    :param component:  The Client/Server Component that is ready.
    :type  tuple: Component (Client/Server)

    :param bind:  The (host, port) the server has bound to.
    :type  tuple: (host, port)
    """

    def __init__(self, component, bind=None):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        args = (component, bind) if bind is not None else (component,)
        super(ready, self).__init__(*args)


class closed(Event):

    """closed Event

    This Event is sent when a server has closed its listening socket.

    .. note::
        This event is for Server components.
    """


class starttls(Event):

    """starttls Event

    This event can be fired to upgrade the socket connection to a TLS
    secured connection.

    .. note::
        This event is currently only available for Server Components.

    :param sock: The client socket where to start TLS.
    :type sock: socket.socket
    """

    def __init__(self, sock):
        super(starttls, self).__init__(sock)
