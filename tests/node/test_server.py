#!/usr/bin/env python
from __future__ import print_function

from time import sleep

import pytest

from circuits import Component, Event
from circuits.net.events import close
from circuits.net.sockets import UDPServer
from circuits.node import Node

pytestmark = pytest.mark.skipif(pytest.PLATFORM == 'win32', reason='Broken on Windows')


class return_value(Event):
    success = True


class App(Component):

    def return_value(self, event):
        print('Hello client!', event.channels)


@pytest.fixture()
def bind(manager, watcher):
    server = UDPServer(0).register(manager)
    assert watcher.wait('ready', channel='server')

    host, port = server.host, server.port

    server.fire(close())
    assert watcher.wait('closed', channel='server')

    server.unregister()
    assert watcher.wait('unregistered', channel='server')

    return host, port


@pytest.fixture()
def app(manager, watcher, bind):
    server = Node(port=bind[1], server_ip=bind[0])
    server.register(manager)
    server.bind = bind
    assert watcher.wait('registered', channel='node')

    return server


def test_auto_reconnect(app, watcher, manager):
    # add client
    client = App().register(manager)
    node = Node().register(client)
    chan = node.add('client1', *app.bind, reconnect_delay=1, connect_timeout=1)
    assert watcher.wait('connected', channel=chan)
    watcher.clear()

    # close server
    app.fire(close(), app.channel)
    assert watcher.wait('closed', channel=app.channel)
    watcher.clear()

    # client gets an unreachable
    assert watcher.wait('connect', channel=chan)
    assert watcher.wait('unreachable', channel=chan)
    watcher.clear()

    # start a new server
    node2 = Node(port=app.bind[1], server_ip=app.bind[0])
    node2.register(manager)
    assert watcher.wait('ready', channel=node2.channel)
    watcher.clear()

    assert watcher.wait('connected', channel=chan)

    client.unregister()


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
    app.server.send(event, app.server.get_socks()[0], no_result=True)
    assert watcher.wait('return_value')

    client1.unregister()
    client2.unregister()


def test_server_send_multicast(app, watcher, manager):
    client1 = App().register(manager)
    node1 = Node().register(client1)
    chan1 = node1.add('client1', *app.bind)
    assert watcher.wait('connected', channel=chan1)
    watcher.clear()

    client2 = App().register(manager)
    node2 = Node().register(client2)
    chan2 = node2.add('client2', *app.bind)
    assert watcher.wait('connected', channel=chan2)
    watcher.clear()

    client3 = App().register(manager)
    node3 = Node().register(client3)
    chan3 = node3.add('client3', *app.bind)
    assert watcher.wait('connected', channel=chan3)
    watcher.clear()

    event = return_value()
    app.server.send_to(event, app.server.get_socks())
    assert watcher.wait('return_value')

    for _ in range(3):
        if watcher.count("return_value") == 3:
            break
        sleep(1)
    assert watcher.count("return_value") == 3

    client1.unregister()
    client2.unregister()
    client3.unregister()
