from circuits import Component


class Client(Component):

    channel = "client"

    def __init__(self, channel=channel):
        super().__init__(channel=channel)

        self.data = ""
        self.error = None
        self.ready = False
        self.closed = False
        self.connected = False
        self.disconnected = False

    async def ready(self, *args):
        self.ready = True

    async def error(self, error):
        self.error = error

    async def connected(self, host, port):
        self.connected = True

    async def disconnect(self, *args):
        return

    async def disconnected(self):
        self.disconnected = True

    async def closed(self):
        self.closed = True

    async def read(self, *args):
        if len(args) == 2:
            _, data = args
        else:
            data = args[0]

        self.data = data
