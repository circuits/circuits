# Module:   events
# Date:     February 17, 2015
# Authors:  Matthieu Chevrier <treemo@hotmail.fr>
#           Yoann Ono Dit Biot <yoann.onoditbiot@gmail.com>

"""Events use on Node package"""

from circuits import Event


class connect_to(Event):
    """Connected to peer"""
    def __init__(self, connection_name, hostname, port, client_channel,
                 client_obj):
        """
        :param connection_name:    Connection name.
        :type connection_name:     str

        :param hostname:    hostname to connect.
        :type hostname:     str

        :param port:    port to connect.
        :type port:     int

        :param client_channel:    Channel used for client event.
        :type client_channel:     str

        :param client_obj:    Client object.
        :type client_obj:     :class:`circuits.net.sockets.Client`
        """
        super(connect_to, self).__init__(
            connection_name, hostname, port, client_channel, client_obj
        )


class disconnect_to(connect_to):
    """Disconnected to peer"""


class remote(Event):
    """send event to peer"""

    def __init__(self, event, connection_name, channel=None):
        """
        :param event:    Event to remote execute.
        :type event:     :class:`circuits.core.events.Event`

        :param connection_name:    Connection name.
        :type connection_name:     str

        :param channel:    Remote channel (channel to use on peer).
        :type channel:     str
        """
        super(remote, self).__init__(event, connection_name, channel=channel)
