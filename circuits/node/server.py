# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""
import itertools

from circuits.net.sockets import TCPServer
from circuits import handler, BaseComponent

from .protocol import Protocol


class Server(BaseComponent):
    """Server

    ...
    """

    channel = 'node'
    __protocol = {}

    def __init__(self, bind, channel=channel, **kwargs):
        super(Server, self).__init__(channel=channel, **kwargs)

        self.server = TCPServer(bind, channel=self.channel, **kwargs)
        self.server.register(self)
        self.__receive_event_firewall = kwargs.get(
            'receive_event_firewall',
            None
        )
        self.__send_event_firewall = kwargs.get(
            'send_event_firewall',
            None
        )

    def send(self, event, sock):
        return self.__protocol[sock].send(event)

    def send_to(self, event, socks):
        for sock in socks:
            self.send(event, sock)

    def send_all(self, event):
        sock = list(self.__protocol)[0]
        for item in self.__protocol[sock].send(event):
            pass

    @handler('read')
    def _on_read(self, sock, data):
        self.__protocol[sock].add_buffer(data)

    @property
    def host(self):
        if hasattr(self, 'server'):
            return self.server.host

    @property
    def port(self):
        if hasattr(self, 'server'):
            return self.server.port

    @handler('connect')
    def __connect_peer(self, sock, host, port):
        self.__protocol[sock] = Protocol(
            sock=sock,
            server=self.server,
            receive_event_firewall=self.__receive_event_firewall,
            send_event_firewall=self.__send_event_firewall,
            channel=self.channel
        ).register(self)

    @handler('disconnect')
    def __disconnect_peer(self, sock):
        for s in self.__protocol.copy():
            try:
                s.getpeername()
            except:
                del(self.__protocol[s])
