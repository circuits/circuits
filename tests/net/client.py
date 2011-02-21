from circuits import Component

class Client(Component):

    channel = "client"

    def __init__(self, channel=channel):
        super(Client, self).__init__(channel=channel)

        self.data = ""
        self.ready = False
        self.connected = False
        self.disconnected = False

    def ready(self, component):
        self.ready = True

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.disconnected = True

    def read(self, data):
        self.data = data
