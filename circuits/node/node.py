"""Node

this module manage node (start server, add peer, ...)
.. seealso:: Examples in :dir:`examples.node`
"""
from circuits import BaseComponent, Timer, handler
from circuits.net.events import connect

from .client import Client
from .events import connected_to, disconnected_from, remote
from .server import Server


class Node(BaseComponent):

    """Node

    this class manage node (start server, add peer, ...)
    .. seealso:: Examples in :dir:`examples.node`
    """
    channel = 'node'
    __peers = {}

    def __init__(self, port=None, channel=channel, **kwargs):
        """Start node system.

        :param port:    An optional keyword argument which if defined,
                        start server on this port.
                        **Default:** ``None`` (don't start the server)
        :type port:     int

        :param server_ip:   An optional keyword argument which define
                            ip where the socket has listen to.
                            **Default:** ``0.0.0.0`` (all ip is allowed)
        :type server_ip:     str

        :param channel: An optional keyword argument which if defined,
                        set channel used for node event. **Default:** ``node``
        :type channel:  str

        :param receive_event_firewall:  An optional keyword argument which if
                                        defined, set function or method to call
                                        to check if event is allowed for sending.
                                        **Default:** ``None`` (no firewall)
        :type receive_event_firewall:   function
        :type receive_event_firewall:   method

        :param send_event_firewall:  An optional keyword argument which if
                                    defined, set function or method to call to
                                    check if event is allowed for executing
                                    **Default:** ``None`` (no firewall)
        :type send_event_firewall:   function
        :type send_event_firewall:   method
        """
        super(Node, self).__init__(channel=channel, **kwargs)

        if port is not None:
            self.server = Server(
                port, channel=channel, **kwargs).register(self)
        else:
            self.server = None

    def add(self, connection_name, hostname, port, **kwargs):
        """Add new peer to the node.

        :param connection_name:    Connection name.
        :type connection_name:     str

        :param hostname:    hostname of the remote node.
        :type hostname:     str

        :param port:    port of the remote node.
        :type port:     int

        :param auto_remote_event:   An optional keyword argument which if
                                    defined, bind events automatically to remote
                                    execution. **Default:** ``{}`` (no events)
        :type auto_remote_event:    dict

        :param channel: An optional keyword argument which if defined,
                        set channel used for client event. If this keyword is
                        not defined the method will generate the channel name
                        automatically.
        :type channel:  str

        :param reconnect_delay: An optional keyword argument which if defined,
                                set auto reconnect delay.
                                **Default:** ``10`` (seconde)
        :type reconnect_delay:  int

        :param receive_event_firewall:  An optional keyword argument which if
                                        defined, function or method to call for
                                        check if event is allowed for sending.
                                        **Default:** ``None`` (no firewall)
        :type receive_event_firewall:   method

        :param send_event_firewall: An optional keyword argument which if
                                    defined, setfunction or method to call to
                                    check if event is allowed for executing
                                    **Default:** ``None`` (no firewall)
        :type send_event_firewall:  method

        :return: Channel used on client event.
        :rtype: str
        """
        # automatic send event to peer
        auto_remote_event = kwargs.pop('auto_remote_event', {})
        for event_name in auto_remote_event:
            for channel in auto_remote_event[event_name]:
                @handler(event_name, channel=channel)
                def event_handle(self, event, *args, **kwargs):
                    yield self.call(remote(event, connection_name))
            self.addHandler(event_handle)

        client_channel = kwargs.pop(
            'channel',
            '%s_client_%s' % (self.channel, connection_name)
        )
        reconnect_delay = kwargs.pop('reconnect_delay', 10)
        client = Client(hostname, port, channel=client_channel, **kwargs)

        # connected event binding
        @handler('connected', channel=client_channel)
        def connected(self, hostname, port):
            self.fire(connected_to(
                connection_name, hostname, port, client_channel, client
            ))
        self.addHandler(connected)

        # disconnected event binding
        @handler('disconnected', 'unreachable', channel=client_channel)
        def disconnected(self, event, *args, **kwargs):
            if event.name == 'disconnected':
                self.fire(disconnected_from(
                    connection_name, hostname, port, client_channel, client
                ))

            # auto reconnect
            if reconnect_delay > 0:
                Timer(
                    reconnect_delay,
                    connect(hostname, port),
                    client_channel
                ).register(self)

        self.addHandler(disconnected)

        client.register(self)
        self.__peers[connection_name] = client
        return client_channel

    def get_connection_names(self):
        """Get connections names

        :return: The list of connections names
        :rtype: list of str
        """
        return list(self.__peers)

    def get_peer(self, connection_name):
        """Get a client object by name

        :param connection_name:    Connection name.
        :type connection_name:     str

        :return: The Client object
        :rtype: :class:`circuits.node.client.Client`
        """
        return self.__peers[connection_name] if connection_name in self.__peers\
            else None

    @handler('remote', channel='*')
    def __on_remote(self, event, remote_event, connection_name, channel=None):
        """Send event to peer

        Event handler to run an event on peer (the event definition is
        :class:`circuits.node.events.remote`)

        :param event:    The event triggered (by the handler)
        :type event:     :class:`circuits.node.events.remote`

        :param remote_event:    Event to execute remotely.
        :type remote_event:     :class:`circuits.core.events.Event`

        :param connection_name:    Connection name (peer selection).
        :type connection_name:     str

        :param channel:    Remote channel (channel to use on peer).
        :type channel:     str

        :return: The result of remote event
        :rtype: generator

        :Example:
        ``# hello is your event to execute remotely
        # peer_test is peer name
        result = yield self.fire(remote(hello())), 'peer_test')
        print(result.value)``
        """
        node = self.__peers[connection_name]
        remote_event.channels = (channel,) if channel is not None \
            else event.channels
        return node.send(remote_event)
