#!/usr/bin/env python

from circuits import handler, Event, Component#, Debugger
from circuits.net.protocols.irc import strip, sourceJoin, sourceSplit, IRC

from circuits.net.protocols.irc import (
        RAW, PASS, USER, NICK, PING, PONG, QUIT,
        JOIN, PART, PRIVMSG, NOTICE, CTCP, CTCPREPLY,
        KICK, TOPIC, MODE, INVITE, NAMES)

class Read(Event):
    """Read Event"""

class App(Component):

    def __init__(self):
        super(App, self).__init__()

        IRC().register(self)

        self.data = []
        self.events = []

    @handler(False)
    def reset(self):
        self.data = []
        self.events = []

    @handler(filter=True)
    def event(self, event, *args, **kwargs):
        self.events.append(event)

    def write(self, data):
        self.data.append(data)

def pytest_funcarg__app(request):
    return request.cached_setup(
            setup=lambda: setupapp(request),
            teardown=lambda app: teardownapp(app),
            scope="module")

def setupapp(request):
    app = App()# + Debugger()
    app.start()

    while app: pass
    app.reset()

    return app

def teardownapp(app):
    app.stop()

###
### Test Functions (utility)
###

def test_strip():
    s = ":\x01\x02test\x02\x01"
    s = strip(s)
    assert s == "\x01\x02test\x02\x01"

    s = ":\x01\x02test\x02\x01"
    s = strip(s, color=True)
    assert s == "test"

def test_sourceJoin():
    nick, ident, host = "test", "foo", "localhost"
    s = sourceJoin(nick, ident, host)
    assert s == "test!foo@localhost"

def test_sourceSplit():
    s = "test!foo@localhost"
    nick, ident, host = sourceSplit(s)
    assert nick == "test"
    assert ident == "foo"
    assert host == "localhost"

    s = "test"
    nick, ident, host = sourceSplit(s)
    assert nick == "test"
    assert ident == None
    assert host == None

###
### Test IRC Commands
###

def test_PASS(app):
    app.reset()

    app.push(PASS("secret"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PASS"
    assert e.args[0] == "secret"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PASS secret"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PASS secret\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PASS secret\r\n"

def test_USER(app):
    app.reset()

    app.push(USER("foo", "localhost", "localhost", "Test Client"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "USER"
    assert e.args[0] == "foo"
    assert e.args[1] == "localhost"
    assert e.args[2] == "localhost"
    assert e.args[3] == "Test Client"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "USER foo \"localhost\" \"localhost\" :Test Client"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "USER foo \"localhost\" \"localhost\" :Test Client\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "USER foo \"localhost\" \"localhost\" :Test Client\r\n"

def test_NICK(app):
    app.reset()

    app.push(NICK("test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "NICK"
    assert e.args[0] == "test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "NICK test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "NICK test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "NICK test\r\n"

def test_PING(app):
    app.reset()

    app.push(PING("localhost"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PING"
    assert e.args[0] == "localhost"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PING :localhost"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PING :localhost\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PING :localhost\r\n"

def test_PONG(app):
    app.reset()

    app.push(PONG("localhost"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PONG"
    assert e.args[0] == "localhost"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PONG :localhost"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PONG :localhost\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PONG :localhost\r\n"

def test_QUIT(app):
    app.reset()

    app.push(QUIT())
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "QUIT"
    assert not e.args

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "QUIT :Leaving"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "QUIT :Leaving\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "QUIT :Leaving\r\n"

    app.reset()

    app.push(QUIT("Test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "QUIT"
    assert e.args[0] == "Test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "QUIT :Test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "QUIT :Test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "QUIT :Test\r\n"

def test_JOIN(app):
    app.reset()

    app.push(JOIN("#test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "JOIN"
    assert e.args[0] == "#test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "JOIN #test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "JOIN #test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "JOIN #test\r\n"

    app.reset()

    app.push(JOIN("#test", "secret"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "JOIN"
    assert e.args[0] == "#test"
    assert e.args[1] == "secret"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "JOIN #test secret"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "JOIN #test secret\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "JOIN #test secret\r\n"

def test_PART(app):
    app.reset()

    app.push(PART("#test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PART"
    assert e.args[0] == "#test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PART #test :Leaving"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PART #test :Leaving\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PART #test :Leaving\r\n"

    app.reset()

    app.push(PART("#test", "Test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PART"
    assert e.args[0] == "#test"
    assert e.args[1] == "Test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PART #test :Test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PART #test :Test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PART #test :Test\r\n"

def test_PRIVMSG(app):
    app.reset()

    app.push(PRIVMSG("test", "Hello"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "PRIVMSG"
    assert e.args[0] == "test"
    assert e.args[1] == "Hello"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PRIVMSG test :Hello"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PRIVMSG test :Hello\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PRIVMSG test :Hello\r\n"

def test_NOTICE(app):
    app.reset()

    app.push(NOTICE("test", "Hello"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "NOTICE"
    assert e.args[0] == "test"
    assert e.args[1] == "Hello"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "NOTICE test :Hello"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "NOTICE test :Hello\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "NOTICE test :Hello\r\n"

def test_CTCP(app):
    app.reset()

    app.push(CTCP("test", "PING", "1234567890"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "CTCP"
    assert e.args[0] == "test"
    assert e.args[1] == "PING"
    assert e.args[2] == "1234567890"

    e = events.next()
    assert e.name == "PRIVMSG"
    assert e.args[0] == "test"
    assert e.args[1] == "PING 1234567890"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PRIVMSG test :PING 1234567890"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PRIVMSG test :PING 1234567890\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PRIVMSG test :PING 1234567890\r\n"

def test_CTCPREPLY(app):
    app.reset()

    app.push(CTCPREPLY("test", "PING", "1234567890"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "CTCPREPLY"
    assert e.args[0] == "test"
    assert e.args[1] == "PING"
    assert e.args[2] == "1234567890"

    e = events.next()
    assert e.name == "NOTICE"
    assert e.args[0] == "test"
    assert e.args[1] == "PING 1234567890"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "NOTICE test :PING 1234567890"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "NOTICE test :PING 1234567890\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "NOTICE test :PING 1234567890\r\n"

def test_KICK(app):
    app.reset()

    app.push(KICK("#test", "test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "KICK"
    assert e.args[0] == "#test"
    assert e.args[1] == "test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "KICK #test test :"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "KICK #test test :\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "KICK #test test :\r\n"

    app.reset()

    app.push(KICK("#test", "test", "Bye"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "KICK"
    assert e.args[0] == "#test"
    assert e.args[1] == "test"
    assert e.args[2] == "Bye"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "KICK #test test :Bye"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "KICK #test test :Bye\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "KICK #test test :Bye\r\n"

def test_TOPIC(app):
    app.reset()

    app.push(TOPIC("#test", "Hello World!"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "TOPIC"
    assert e.args[0] == "#test"
    assert e.args[1] == "Hello World!"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "TOPIC #test :Hello World!"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "TOPIC #test :Hello World!\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "TOPIC #test :Hello World!\r\n"

def test_MODE(app):
    app.reset()

    app.push(MODE("+i"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "MODE"
    assert e.args[0] == "+i"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "MODE :+i"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "MODE :+i\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "MODE :+i\r\n"

    app.reset()

    app.push(MODE("+o test", "#test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "MODE"
    assert e.args[0] == "+o test"
    assert e.args[1] == "#test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "MODE #test :+o test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "MODE #test :+o test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "MODE #test :+o test\r\n"

def test_INVITE(app):
    app.reset()

    app.push(INVITE("test", "#test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "INVITE"
    assert e.args[0] == "test"
    assert e.args[1] == "#test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "INVITE test #test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "INVITE test #test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "INVITE test #test\r\n"

def test_NAMES(app):
    app.reset()

    app.push(NAMES())
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "NAMES"
    assert not e.args

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "NAMES"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "NAMES\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "NAMES\r\n"

    app.reset()

    app.push(NAMES("#test"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "NAMES"
    assert e.args[0] == "#test"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "NAMES #test"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "NAMES #test\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "NAMES #test\r\n"

###
### Test IRC Responses
###

def test_ping(app):
    app.reset()

    app.push(Read("PING :localhost\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == "PING :localhost\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == "PING :localhost"

    e = events.next()
    assert e.name == "Ping"
    assert e.args[0] == "localhost"

    e = events.next()
    assert e.name == "PONG"
    assert e.args[0] == "localhost"

    e = events.next()
    assert e.name == "RAW"
    assert e.args[0] == "PONG :localhost"

    e = events.next()
    assert e.name == "Write"
    assert e.args[0] == "PONG :localhost\r\n"

    data = iter(app.data)

    s = data.next()
    assert s == "PONG :localhost\r\n"

def test_numerics(app):
    app.reset()

    app.push(Read(":localhost 001 test " +
        ":Welcome to the circuits Internet Relay Chat Network test\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":localhost 001 test " \
            ":Welcome to the circuits Internet Relay Chat Network test\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":localhost 001 test " \
            ":Welcome to the circuits Internet Relay Chat Network test"

    e = events.next()
    assert e.name == "Numeric"
    assert e.args[0] == "localhost"
    assert e.args[1] == "test"
    assert e.args[2] == 1
    assert e.args[3] == None
    assert e.args[4] == \
            "Welcome to the circuits Internet Relay Chat Network test"

    app.reset()

    app.push(Read(":localhost 332 test #test :Hello World!\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":localhost 332 test #test :Hello World!\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":localhost 332 test #test :Hello World!"

    e = events.next()
    assert e.name == "Numeric"
    assert e.args[0] == "localhost"
    assert e.args[1] == "test"
    assert e.args[2] == 332
    assert e.args[3] == "#test"
    assert e.args[4] == "Hello World!"

def test_ctcp(app):
    app.reset()

    app.push(Read(":test!foo@localhost PRIVMSG test :TIME\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost PRIVMSG test :TIME\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost PRIVMSG test :TIME"

    e = events.next()
    assert e.name == "Ctcp"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "test"
    assert e.args[2] == "TIME"
    assert e.args[3] == ""

def test_message(app):
    app.reset()

    app.push(Read(":test!foo@localhost PRIVMSG test :Hello\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost PRIVMSG test :Hello\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost PRIVMSG test :Hello"

    e = events.next()
    assert e.name == "Message"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "test"
    assert e.args[2] == "Hello"

def test_notice(app):
    app.reset()

    app.push(Read(":test!foo@localhost NOTICE test :Hello\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost NOTICE test :Hello\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost NOTICE test :Hello"

    e = events.next()
    assert e.name == "Notice"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "test"
    assert e.args[2] == "Hello"

def test_join(app):
    app.reset()

    app.push(Read(":test!foo@localhost JOIN #test\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost JOIN #test\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost JOIN #test"

    e = events.next()
    assert e.name == "Join"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "#test"

def test_part(app):
    app.reset()

    app.push(Read(":test!foo@localhost PART #test :Leaving\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost PART #test :Leaving\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost PART #test :Leaving"

    e = events.next()
    assert e.name == "Part"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "#test"
    assert e.args[2] == "Leaving"

def test_quit(app):
    app.reset()

    app.push(Read(":test!foo@localhost QUIT :Leaving\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost QUIT :Leaving\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost QUIT :Leaving"

    e = events.next()
    assert e.name == "Quit"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "Leaving"

def test_nick(app):
    app.reset()

    app.push(Read(":test!foo@localhost NICK :test_\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost NICK :test_\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost NICK :test_"

    e = events.next()
    assert e.name == "Nick"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "test_"

def test_mode(app):
    app.reset()

    app.push(Read(":test!foo@localhost MODE #test +o test\r\n"))
    while app: pass

    events = iter(app.events)

    e = events.next()
    assert e.name == "Read"
    assert e.args[0] == ":test!foo@localhost MODE #test +o test\r\n"

    e = events.next()
    assert e.name == "Line"
    assert e.args[0] == ":test!foo@localhost MODE #test +o test"

    e = events.next()
    assert e.name == "Mode"
    assert e.args[0] == ("test", "foo", "localhost")
    assert e.args[1] == "#test"
    assert e.args[2] == "+o test"
