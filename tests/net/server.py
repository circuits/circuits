from circuits import Component
from circuits.net.events import write


class Server(Component):
    channel = 'server'

    def init(self) -> None:
        self.data = ''
        self.host = None
        self.port = None
        self.client = None
        self.ready = False
        self.closed = False
        self.connected = False
        self.disconnected = False

    def ready(self, server, bind) -> None:
        self.ready = True
        self.host, self.port = bind

    def close(self) -> None:
        return

    def closed(self) -> None:
        self.closed = True

    def connect(self, sock, *args) -> None:
        self.connected = True
        self.client = args
        self.fire(write(sock, b'Ready'))

    def disconnect(self, sock) -> None:
        self.client = None
        self.disconnected = True

    def read(self, sock, data):
        self.data = data
        return data
