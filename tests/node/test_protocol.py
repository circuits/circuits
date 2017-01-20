#!/usr/bin/env python
import pytest

from circuits import Component, Event
from circuits.core import Value
from circuits.node.protocol import Protocol
from circuits.node.utils import dump_event, dump_value

pytestmark = pytest.mark.skipif(pytest.PLATFORM == 'win32', reason='Broken on Windows')


class return_value(Event):
    success = True


class firewall_block(Event):
    pass


class AppClient(Component):
    write_data = b''

    def return_value(self):
        return 'Hello server!'

    def write(self, data):
        self.write_data = data


class AppFirewall(Component):
    write_data = b''

    def fw_receive(self, event, sock):
        return self.__event_is_allow(event)

    def fw_send(self, event, sock):
        return self.__event_is_allow(event)

    def write(self, data):
        self.write_data = data

    def __event_is_allow(self, event):
        allow = 'return_value' == event.name \
            and 'prohibits_channel' not in event.channels

        if not allow:
            self.fire(firewall_block())

        return allow


class AppServer(Component):
    write_data = b''
    write_sock = None

    def return_value(self):
        return 'Hello client!'

    def write(self, sock, data):
        self.write_sock = sock
        self.write_data = data


@pytest.fixture()
def app_client(request, manager, watcher):
    app = AppClient()
    app.register(manager)
    watcher.wait('registered')

    app.protocol = Protocol().register(app)
    watcher.wait('registered')

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


@pytest.fixture()
def app_firewall(request, manager, watcher):
    app = AppFirewall()
    app.register(manager)
    watcher.wait('registered')

    app.protocol = Protocol(
        sock='sock obj',
        receive_event_firewall=app.fw_receive,
        send_event_firewall=app.fw_send,
    ).register(app)
    watcher.wait('registered')

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


@pytest.fixture()
def app_server(request, manager, watcher):
    app = AppServer()
    app.register(manager)
    watcher.wait('registered')

    app.protocol = Protocol(sock='sock obj', server=True).register(app)
    watcher.wait('registered')

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_add_buffer(app_client, watcher):
    packet = str.encode(dump_event(return_value(), 1))
    app_client.protocol.add_buffer(packet)
    assert watcher.wait('return_value_success')
    assert watcher.wait('write')

    value = Value()
    value.value = 'Hello server!'
    value.errors = False
    value.node_call_id = 1
    assert app_client.write_data == str.encode(dump_value(value) + '~~~')


def test_add_buffer_server(app_server, watcher):
    packet = str.encode(dump_event(return_value(), 1))
    app_server.protocol.add_buffer(packet)
    assert watcher.wait('return_value_success')
    assert watcher.wait('write')

    value = Value()
    value.value = 'Hello client!'
    value.errors = False
    value.node_call_id = 1
    assert app_server.write_data == str.encode(dump_value(value) + '~~~')
    assert app_server.write_sock == 'sock obj'


def test_firewall_receive(app_firewall, watcher):
    # good event
    packet = str.encode(dump_event(return_value(), 1))
    app_firewall.protocol.add_buffer(packet)
    assert watcher.wait('return_value')

    # bad name
    packet = str.encode(dump_event(Event.create('unallow_event'), 1))
    app_firewall.protocol.add_buffer(packet)
    assert watcher.wait('firewall_block')

    # bad channel
    event = return_value()
    event.channels = ('prohibits_channel',)
    packet = str.encode(dump_event(event, 1))
    app_firewall.protocol.add_buffer(packet)
    assert watcher.wait('firewall_block')


def test_firewall_send(app_firewall, watcher):
    # good event
    event = return_value()
    generator = app_firewall.protocol.send(event)
    next(generator)  # exec
    assert watcher.wait('write')
    assert app_firewall.write_data == str.encode(dump_event(event, 0) + '~~~')

    # bad name
    generator = app_firewall.protocol.send(Event.create('unallow_event'))
    next(generator)  # exec
    assert watcher.wait('firewall_block')

    # bad channel
    event = return_value()
    event.channels = ('prohibits_channel',)
    generator = app_firewall.protocol.send(event)
    next(generator)  # exec
    assert watcher.wait('firewall_block')


def test_send(app_client, watcher):
    event = return_value()
    generator = app_client.protocol.send(event)
    next(generator)  # exec

    assert watcher.wait('write')
    assert app_client.write_data == str.encode(dump_event(event, 0) + '~~~')

    value = Value()
    value.value = 'Hello server!'
    value.errors = False
    value.node_call_id = 0
    app_client.protocol.add_buffer(str.encode(dump_value(value) + '~~~'))

    assert next(generator).getValue() == value.value


def test_send_server(app_server, watcher):
    event = return_value()
    generator = app_server.protocol.send(event)
    next(generator)  # exec

    assert watcher.wait('write')
    assert app_server.write_data == str.encode(dump_event(event, 0) + '~~~')
    assert app_server.write_sock == 'sock obj'

    value = Value()
    value.value = 'Hello client!'
    value.errors = False
    value.node_call_id = 0
    app_server.protocol.add_buffer(str.encode(dump_value(value) + '~~~'))

    assert next(generator).getValue() == value.value
