from circuits import Component
from circuits.net.sockets import Write

class Server(Component):

    channel = "server"

    def __init__(self):
        super(Server, self).__init__()

        self.data = ""
        self.connected = False
        self.disconnected = False

    def connect(self, sock, *args):
        self.connected = True
        self.push(Write(sock, "Ready"))

    def disconnect(self, sock):
        self.disconnected = True

    def read(self, sock, data):
        self.data = data
