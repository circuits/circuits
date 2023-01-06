#!/usr/bin/env python
from pytest import PLATFORM, fixture, skip

from circuits import Component, Event
from circuits.net.events import close
from circuits.net.sockets import UDPServer
from circuits.node import Node, remote

if PLATFORM == 'win32':
    skip('Broken on Windows')


class App(Component):

    ready = False
    value = False
    disconnected = False

    def foo(self):
        return 'Hello World!'

    def ready(self, *args):
        self.ready = True

    def disconnect(self, component):
        self.disconnected = True

    def remote_value_changed(self, value):
        self.value = True


@fixture()
def bind(request, simple_manager):
    server = UDPServer(0).register(simple_manager)
    assert simple_manager.run_until("ready")

    host, port = server.host, server.port

    server.fire(close())
    assert simple_manager.run_until("closed")

    server.unregister()
    assert simple_manager.run_until("unregistered")

    return host, port


@fixture()
def app(request, manager, watcher, bind):
    app = App().register(manager)
    node = Node().register(app)
    assert watcher.wait('ready')

    child = (App() + Node(port=bind[1], server_ip=bind[0]))
    child.start(process=True)

    node.add('child', *bind)
    assert watcher.wait('connected')

    def finalizer():
        child.stop()

    request.addfinalizer(finalizer)

    return app


def test_return_value(app, watcher):
    event = Event.create('foo')
    event.notify = True

    remote_event = remote(event, 'child')
    remote_event.notify = True

    value = app.fire(remote_event)
    assert watcher.wait('remote_value_changed')
    assert value.value == 'Hello World!'
