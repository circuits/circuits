import pytest

from circuits import Component, Event
from circuits.net.sockets import Close
from circuits.node import Node, Remote
from circuits.net.sockets import UDPServer
from circuits.core.events import Unregister


class Foo(Event):
    """Foo Event"""


class App(Component):
    disconnected = False
    ready = False
    value = False

    def foo(self):
        return "Hello World!"

    def ready(self, component):
        self.ready = True

    def disconnect(self, component):
        self.disconnected = True

    def remote_value_changed(self, value):
        self.value = True


def get_free_port(manager):
    server = UDPServer(0)
    server.register(manager)
    assert pytest.wait_for(manager, "ready")
    host, port = server.host, server.port
    manager.fire(Close())
    assert pytest.wait_for(manager, "disconnected")
    manager.fire(Unregister(server))
    return host, port


def test_return_value():
    a1 = App()
    n1 = Node().register(a1)
    a1.start()

    host, port = get_free_port(a1)
    (App() + Node((host, port))).start(process=True)

    n1.add('bar', host, port)

    e = Event.create('foo')
    e.notify = True
    r = Remote(e, 'bar')
    r.notify = True
    value = a1.fire(r)

    assert pytest.wait_for(a1, "value")

    assert value.value == "Hello World!"
