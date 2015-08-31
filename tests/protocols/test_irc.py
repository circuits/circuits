#!/usr/bin/env python


import pytest
from pytest import fixture


from circuits.six import b, u

from circuits import handler, Event, Component

from circuits.net.events import read, write

from circuits.protocols.irc import IRC
from circuits.protocols.irc import strip, joinprefix, parsemsg, parseprefix

from circuits.protocols.irc import (
    PASS, USER, NICK, PONG, QUIT,
    JOIN, PART, PRIVMSG, NOTICE, AWAY,
    KICK, TOPIC, MODE, INVITE, NAMES, WHOIS
)


class App(Component):

    def init(self):
        IRC().register(self)

        self.data = []
        self.events = []

    @handler(False)
    def reset(self):
        self.data = []
        self.events = []

    @handler()
    def _on_event(self, event, *args, **kwargs):
        self.events.append(event)

    def request(self, message):
        self.fire(write(bytes(message)))

    def write(self, data):
        self.data.append(data)


@fixture(scope="function")
def app(request):
    app = App()

    while len(app):
        app.flush()

    return app


def test_strip():
    s = ":\x01\x02test\x02\x01"
    s = strip(s)
    assert s == "\x01\x02test\x02\x01"

    s = ":\x01\x02test\x02\x01"
    s = strip(s, color=True)
    assert s == "test"


def test_joinprefix():
    nick, ident, host = "test", "foo", "localhost"
    s = joinprefix(nick, ident, host)
    assert s == "test!foo@localhost"


def test_parsemsg():
    s = b(":foo!bar@localhost NICK foobar")
    source, command, args = parsemsg(s)
    assert source == (u("foo"), u("bar"), u("localhost"))
    assert command == "NICK"
    assert args == [u("foobar")]

    s = b("")
    source, command, args = parsemsg(s)
    assert source == (None, None, None)
    assert command is None
    assert args == []


def test_parseprefix():
    s = "test!foo@localhost"
    nick, ident, host = parseprefix(s)
    assert nick == "test"
    assert ident == "foo"
    assert host == "localhost"

    s = "test"
    nick, ident, host = parseprefix(s)
    assert nick == "test"
    assert ident is None
    assert host is None


@pytest.mark.parametrize("event,data", [
    (PASS("secret"), b"PASS secret\r\n"),
    (
        USER("foo", "localhost", "localhost", "Test Client"),
        b"USER foo localhost localhost :Test Client\r\n"
    ),
    (NICK("test"), b"NICK test\r\n"),
    (PONG("localhost"), b"PONG :localhost\r\n"),
    (QUIT(), b"QUIT Leaving\r\n"),
    (QUIT("Test"), b"QUIT Test\r\n"),
    (QUIT("Test Message"), b"QUIT :Test Message\r\n"),
    (JOIN("#test"), b"JOIN #test\r\n"),
    (JOIN("#test", "secret"), b"JOIN #test secret\r\n"),
    (PART("#test"), b"PART #test\r\n"),
    (PRIVMSG("test", "Hello"), b"PRIVMSG test Hello\r\n"),
    (PRIVMSG("test", "Hello World"), b"PRIVMSG test :Hello World\r\n"),
    (NOTICE("test", "Hello"), b"NOTICE test Hello\r\n"),
    (NOTICE("test", "Hello World"), b"NOTICE test :Hello World\r\n"),
    (KICK("#test", "test"), b"KICK #test test :\r\n"),
    (KICK("#test", "test", "Bye"), b"KICK #test test Bye\r\n"),
    (KICK("#test", "test", "Good Bye!"), b"KICK #test test :Good Bye!\r\n"),
    (TOPIC("#test", "Hello World!"), b"TOPIC #test :Hello World!\r\n"),
    (MODE("+i"), b"MODE +i\r\n"),
    (MODE("#test", "+o", "test"), b"MODE #test +o test\r\n"),
    (INVITE("test", "#test"), b"INVITE test #test\r\n"),
    (NAMES(), b"NAMES\r\n"),
    (NAMES("#test"), b"NAMES #test\r\n"),
    (AWAY("I am away."), b"AWAY :I am away.\r\n"),
    (WHOIS("somenick"), b"WHOIS :somenick\r\n"),
])
def test_commands(event, data):
    message = event.args[0]
    return bytes(message) == data


@pytest.mark.parametrize("data,event", [
    (
        b":localhost NOTICE * :*** Looking up your hostname...\r\n",
        Event.create(
            "notice", (u("localhost"), None, None), u("*"),
            u("*** Looking up your hostname..."),
        )
    ),
])
def test_responses(app, data, event):
    app.reset()
    app.fire(read(data))
    while len(app):
        app.flush()

    e = app.events[-1]

    assert event.name == e.name
    assert event.args == e.args
    assert event.kwargs == e.kwargs
