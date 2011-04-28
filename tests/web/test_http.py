import pytest

from circuits.web import Server, Controller
from circuits.web.client import parse_url
from circuits.net.sockets import TCPServer, TCPClient
from circuits.net.sockets import Close, Connect, Write
from circuits import Component
from circuits import Debugger

class Client(Component):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self._buffer = []
        self.done = False

    def read(self, data):
        self._buffer.append(data)
        if data.find(b"\r\n") != -1:
            self.done = True

    def buffer(self):
        return b''.join(self._buffer)

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    transport = TCPClient()
    client = Client()
    client += transport + Debugger()
    client.start()

    host, port, resource, secure = parse_url(webapp.server.base)
    client.push(Connect(host, port))
    assert pytest.wait_for(transport, "connected")

    client.push(Write(b"GET / HTTP/1.1\r\n"))
    client.push(Write(b"Content-Type: text/plain\r\n\r\n"))
    assert pytest.wait_for(client, "done")

    client.stop()

    s = client.buffer().decode('utf-8').split('\r\n')[0]
    assert s == "HTTP/1.1 200 OK"
