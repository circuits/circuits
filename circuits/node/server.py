from circuits import BaseComponent, handler
from circuits.net.sockets import TCPServer

from .protocol import Protocol


class Server(BaseComponent):

    """Node server."""

    channel = 'node'
    __protocols = {}

    def __init__(self, port, server_ip='0.0.0.0', channel=channel,
                 receive_event_firewall=None, send_event_firewall=None,
                 **kwargs):
        """Create server on node system.

        :param port:    start server on this port.
        :type port:     int

        :param server_ip:   An optional keyword argument which which define
                            ip where the socket has listen to.
                            **Default:** ``0.0.0.0`` (all ip is allowed)
        :type server_ip:     str

        :param channel: An optional keyword argument which if defined,
                        set channel used for node event. **Default:** ``node``
        :type channel:  str

        :param receive_event_firewall: An optional keyword argument which if
                                       defined, set function or method to call
                                       to check if event is allowed for sending
                                       **Default:** ``None`` (no firewall)
        :type receive_event_firewall:  function
        :type receive_event_firewall:  method

        :param send_event_firewall:  An optional keyword argument which if
                                    defined, set function or method to call to
                                    check if event is allowed for executing
                                    **Default:** ``None`` (no firewall)
        :type send_event_firewall:   function
        :type send_event_firewall:   method
        """
        super(Server, self).__init__(channel=channel, **kwargs)

        bind = (server_ip, port)
        self.server = TCPServer(bind, channel=self.channel, **kwargs)
        self.server.register(self)
        self.__receive_event_firewall = receive_event_firewall
        self.__send_event_firewall = send_event_firewall

    def send(self, event, sock, no_result=False):
        """Send event to peer

        :param event:    Event to execute remotely.
        :type event:     :class:`circuits.core.events.Event`

        :param sock:    Client's socket (peer selection).
        :type sock:     :class:`socket.socket`

        :param no_result:   An optional keyword argument which if True
                            don't return the event result.
                            **Default:** ``False`` (wait the result)
        :type no_result:     bool

        :return: The result of remote event
        :rtype: generator
        """
        iterator = self.__protocols[sock].send(event)
        if no_result:
            event.node_without_result = True
            try:
                next(iterator)
            except StopIteration:
                pass
        return iterator

    def send_to(self, event, socks):
        """Send event to multiple peer

        :param event:    Event to execute remotely.
        :type event:     :class:`circuits.core.events.Event`

        :param socks:    Client's socket list (peer selection).
        :type socks:     list of :class:`socket.socket`
        """
        for sock in socks:
            self.send(event, sock, no_result=True)

    def send_all(self, event):
        """Send event to all peer

        :param event:    Event to execute remotely.
        :type event:     :class:`circuits.core.events.Event`
        """
        self.send_to(event, list(self.__protocols))

    @handler('read')
    def _on_read(self, sock, data):
        self.__protocols[sock].add_buffer(data)

    @property
    def host(self):
        if hasattr(self, 'server'):
            return self.server.host

    @property
    def port(self):
        if hasattr(self, 'server'):
            return self.server.port

    def get_socks(self):
        """Get clients sockets list

        :return: The list of client socket
        :rtype: list of :class:`socket.socket`
        """
        return list(self.__protocols)

    @handler('connect')
    def __connect_peer(self, sock, host, port):
        self.__protocols[sock] = Protocol(
            sock=sock,
            server=self.server,
            receive_event_firewall=self.__receive_event_firewall,
            send_event_firewall=self.__send_event_firewall,
            channel=self.channel
        ).register(self)

    @handler('disconnect')
    def __disconnect_peer(self, sock):
        for s in self.__protocols.copy():
            try:
                s.getpeername()
            except Exception:
                del self.__protocols[s]
