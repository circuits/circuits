
from circuits.web import Server, Controller

from circuits.web.client import Client, Connect, Request

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    client = Client(webapp.server.base)
    client.start()

    client.push(Connect())
    while not client.connected: pass

    client.push(Request("GET", "/"))
    while client.response is None: pass

    client.stop()

    response = client.response
    assert response.status == 200
    assert response.message == "OK"

    s = response.read()
    assert s == "Hello World!"
