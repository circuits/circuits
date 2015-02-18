#!/usr/bin/env python


from pytest import PLATFORM, skip, fixture
from circuits import Event, Component, handler
from circuits.net.events import close
from circuits.net.sockets import UDPServer
from circuits.node import Node

if PLATFORM == 'win32':
    skip('Broken on Windows')


class return_value(Event):
    success = True


class App(Component):
    def return_value(self, event):
        print('Hello client!', event.channels)


@fixture()
def bind(request, manager, watcher):
    server = UDPServer(0).register(manager)
    assert watcher.wait('ready', channel='server')

    host, port = server.host, server.port

    server.fire(close())
    assert watcher.wait('closed', channel='server')

    server.unregister()
    assert watcher.wait('unregistered', channel='server')

    return host, port


@fixture()
def app(request, manager, watcher, bind):
    server = Node(bind)
    server.register(manager)
    assert watcher.wait('ready', channel='node')

    return server


def test_server_send_all(app, watcher, manager):
    client1 = App().register(manager)
    node1 = Node().register(client1)
    chan = node1.add('client1', *app.bind)
    assert watcher.wait('connected', channel=chan)

    client2 = App().register(manager)
    node2 = Node().register(client2)
    chan = node2.add('client2', *app.bind)
    assert watcher.wait('connected', channel=chan)

    event = return_value()
    app.server.send_all(event)
    assert watcher.wait('return_value')

    client1.unregister()
    client2.unregister()


def test_server_send(app, watcher, manager):
    client1 = App().register(manager)
    node1 = Node().register(client1)
    chan1 = node1.add('client1', *app.bind)
    assert watcher.wait('connected', channel=chan1)


    client2 = App().register(manager)
    node2 = Node().register(client2)
    chan2 = node2.add('client2', *app.bind)
    assert watcher.wait('connected', channel=chan2)

    event = return_value()
    app.server.send(event, app.server.get_socks()[0], noresult=True)
    assert watcher.wait('return_value')
    watcher.clear()
    assert not watcher.wait('return_value')

    client1.unregister()
    client2.unregister()


def test_server_send_multicast(app, watcher, manager):
    client1 = App().register(manager)
    node1 = Node().register(client1)
    chan1 = node1.add('client1', *app.bind)
    assert watcher.wait('connected', channel=chan1)


    client2 = App().register(manager)
    node2 = Node().register(client2)
    chan2 = node2.add('client2', *app.bind)
    assert watcher.wait('connected', channel=chan2)

    client3 = App().register(manager)
    node3 = Node().register(client3)
    chan3 = node3.add('client3', *app.bind)
    assert watcher.wait('connected', channel=chan3)

    event = return_value()
    app.server.send_to(event, app.server.get_socks()[:2])
    assert watcher.wait('return_value')

    event_cnt = 0
    with watcher._lock:
        for event in watcher.events:
            if event.name == 'return_value':
                event_cnt += 1

    assert event_cnt == 2

    client1.unregister()
    client2.unregister()
    client3.unregister()