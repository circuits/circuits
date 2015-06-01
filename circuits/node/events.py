from circuits import Event


class connected_to(Event):

    """Connected to a peer"""

    def __init__(self, connection_name, hostname, port, client_channel,
                 client_obj):
        """
        :param connection_name:    Connection name.
        :type connection_name:     str

        :param hostname:    hostname of the remote system.
        :type hostname:     str

        :param port:    connection port of the remote system.
        :type port:     int

        :param client_channel:    Channel used for client event.
        :type client_channel:     str

        :param client_obj:    Client object.
        :type client_obj:     :class:`circuits.net.sockets.Client`
        """
        super(connected_to, self).__init__(
            connection_name, hostname, port, client_channel, client_obj
        )


class disconnected_from(connected_to):

    """Disconnected from a peer"""


class remote(Event):

    """send event to a peer"""

    def __init__(self, event, connection_name, channel=None):
        """
        :param event:    Event to execute remotely.
        :type event:     :class:`circuits.core.events.Event`

        :param connection_name:    Connection name.
        :type connection_name:     str

        :param channel:    Remote channel (channel to use on peer).
        :type channel:     str
        """
        super(remote, self).__init__(event, connection_name, channel=channel)
