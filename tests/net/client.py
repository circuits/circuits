from circuits import Component


class Client(Component):
    channel = 'client'

    def __init__(self, channel=channel) -> None:
        super().__init__(channel=channel)

        self.data = ''
        self.error = None
        self.ready = False
        self.closed = False
        self.connected = False
        self.disconnected = False

    def ready(self, *args) -> None:
        self.ready = True

    def error(self, error) -> None:
        self.error = error

    def connected(self, host, port) -> None:
        self.connected = True

    def disconnect(self, *args) -> None:
        return

    def disconnected(self) -> None:
        self.disconnected = True

    def closed(self) -> None:
        self.closed = True

    def read(self, *args) -> None:
        if len(args) == 2:
            _, data = args
        else:
            data = args[0]

        self.data = data
