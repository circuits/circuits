from circuits import Component

class Client(Component):

    channel = "client"

    def __init__(self):
        super(Client, self).__init__()

        self.data = ""
        self.connected = False
        self.disconnected = False

    def connected(self, host, port):
        self.connected = True

    def disconnected(self):
        self.disconnected = True

    def read(self, data):
        self.data = data
