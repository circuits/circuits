# Module:   events
# Date:     February 17, 2015
# Authors:  Matthieu Chevrier <treemo@hotmail.fr>
#           Yoann Ono Dit Biot <yoann.onoditbiot@gmail.com>

"""
This module defines the node client class.
"""

from circuits.net.sockets import TCPClient
from circuits import handler, BaseComponent
from circuits.net.events import close, connect

from .protocol import Protocol


class Client(BaseComponent):
    """Node Client (peer)"""
    channel = "node_client"

    def __init__(self, host, port, channel=channel,
                 receive_event_firewall=None, send_event_firewall=None,
                 **kwargs):
        """Add connection to new peer.

        :param hostname:    hostname to connect.
        :type hostname:     str

        :param port:    port to connect.
        :type port:     int

        :param channel: An optional keyword argument which if defined,
                        set channel used for node event.
                        **Default:** ``node_client``
        :type channel:  str

        :param receive_event_firewall:  An optional keyword argument which if
                                        defined, function or method to call for
                                        check if event is allowed for sending.
                                        **Default:** ``None`` (no firewall)
        :type receive_event_firewall:   function
        :type receive_event_firewall:   method

        :param send_event_firewall:  An optional keyword argument which if
                                    defined, function or method to call for
                                    check if event is allowed for executing
                                    **Default:** ``None`` (no firewall)
        :type send_event_firewall:   function
        :type send_event_firewall:   method
        """
        super(Client, self).__init__(channel=channel, **kwargs)

        self.__host = host
        self.__port = port
        self.__protocol = Protocol(
            receive_event_firewall=receive_event_firewall,
            send_event_firewall=send_event_firewall,
        ).register(self)

        TCPClient(channel=self.channel, **kwargs).register(self)

    @handler("ready")
    def _on_ready(self, component):
        self.connect()

    def close(self):
        """Close this connection"""
        self.fire(close())

    def connect(self):
        """Connect to peer"""
        self.fire(connect(self.__host, self.__port))

    def send(self, event):
        """Send event to peer

        :param event:    Event to execute remotely.
        :type event:     :class:`circuits.core.events.Event`

        :return: The result of remote event
        :rtype: generator
        """
        return self.__protocol.send(event)

    @handler("read")
    def _on_read(self, data):
        self.__protocol.add_buffer(data)
