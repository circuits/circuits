# Module:   event
# Date:     23rd June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core Test Suite

Test all functionality of the event library.
"""

import unittest

from circuits import handler, Manager, Component, Event

class Test(Event):
    """Test(Event) -> Test Event"""

class FilterComponent(Component):

    @handler("foo", filter=True)
    def onFOO(self, msg=""):
        return True

    @handler("bar", filter=True)
    def onBAR(self, msg=""):
        if msg.lower() == "hello world":
            return True

class ListenerComponent(Component):

    def foo(self, test, msg=""):
        if msg.lower() == "start":
            self.push(Test(msg="foo"), "foo")

    def bar(self, event, test, msg=""):
        if msg.lower() == "test":
            self.push(Test(msg="hello world"), event._channel)

class Foo(Component):

    flag = False
    gotbar = False

    @handler("test")
    def onTEST(self, event, *args, **kwargs):
        self.flag = True

    @handler("foo")
    def onFOO(self, event):
        self.send(Test(), "bar")

    @handler("gotbar")
    def onGOTBAR(self, event, *args):
        self.gotbar = True


class Bar(Component):

    @handler("bar")
    def onBAR(self, event, *args, **kwargs):
        self.send(Test(), "gotbar")

class EventTestCase(unittest.TestCase):

    def testManagerRepr(self):
        """Test Manager.__repr__

        Test Manager's representation string.
        """

        x = Manager()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 0 h: 0) [S]>")

        a = Foo()
        x += a
        self.assertEquals(repr(x), "<Manager (q: 1 c: 3 h: 3) [S]>")

        x.flush()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 4 h: 3) [S]>")

        x.push(Test(), "foo")
        self.assertEquals(repr(x), "<Manager (q: 1 c: 4 h: 3) [S]>")

        x.flush()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 4 h: 3) [S]>")

        x -= a
        self.assertEquals(repr(x), "<Manager (q: 1 c: 0 h: 0) [S]>")


    def testComponentRepr(self):
        """Test Component.__repr__

        Test Component's representation string.
        """

        a = Foo()
        self.assertEquals(repr(a), "<Foo/ (q: 0 c: 3 h: 3) [S]>")

        a.push(Test(), "foo")
        self.assertEquals(repr(a), "<Foo/ (q: 1 c: 3 h: 3) [S]>")

        a.flush()
        self.assertEquals(repr(a), "<Foo/ (q: 0 c: 4 h: 3) [S]>")


    def testComponentSetup(self):
        """Test Component Setup

        Tests that filters and listeners of a Component are
        automatically added to the event manager instnace
        given.
        """

        manager = Manager()

        filter = FilterComponent()
        manager += filter
        listener = ListenerComponent()
        manager += listener

        self.assertTrue(filter.onFOO in manager.channels["foo"])
        self.assertTrue(listener.foo in manager.channels["foo"])
        self.assertTrue(filter.onBAR in manager.channels["bar"])
        self.assertTrue(listener.bar in manager.channels["bar"])

        filter.unregister()
        listener.unregister()

        self.assertEquals(len(manager._handlers), 0)


    def testFilterOrder(self):
        """Test Filter Order

        Test that Events Handlers set as Filters are added and sorted
        such that Filters preceed non-filters.
        """

        class Foo(Component):

            @handler("a")
            def a1(self):
                pass

            @handler("a", filter=True)
            def a2(self):
                pass

            @handler("a")
            def a3(self):
                pass

        foo = Foo()
        self.assertTrue(foo.channels["a"][0] == foo.a2)

    def testTargetsAndChannels(self):
        """Test Components, Targets and Channels

        Test that Components can be set up with a channel
        and that event handlers of that Component work
        correctly. That is, Components that have their
        own channel, have their own global channel and
        each channel is unique to that Component.
        """

        class Foo(Component):

            channel = "foo"

            flag = False

            @handler(filter=True)
            def onALL(self, event, *args, **kwargs):
                self.flag = True
                return True

            @handler("foo")
            def onFOO(self):
                self.flag = False

        class Bar(Component):

            flag = False

            @handler("bar")
            def onBAR(self):
                self.flag = True

        manager = Manager()
        foo = Foo()
        bar = Bar()
        manager += foo
        manager += bar

        manager.send(Event(), "foo", foo.channel)
        self.assertTrue(foo.flag)
        manager.send(Event(), "bar")
        self.assertTrue(bar.flag)

        foo.unregister()
        bar.unregister()

    def testMultipleChannels(self):
        """Test Multiple Channels

        Test that Event Handlers can listen on Multiple
        Channels.
        """

        class Foo(Component):

            flag = False

            @handler("foo", "bar")
            def onFOOBAR(self, event, *args, **kwargs):
                self.flag = True

        manager = Manager()
        foo = Foo()
        manager += foo

        manager.send(Event(), "foo")
        self.assertTrue(foo.flag)
        foo.flag = False

        manager.send(Event(), "bar")
        self.assertTrue(foo.flag)
        foo.flag = False

        foo.unregister()


    def testAllChannels(self):
        """Test All Channels

        Test that Events can be sent to all channels.
        """

        class A(Component):

            channel = "A"

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        class B(Component):

            channel = "B"

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        class C(Component):

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        x = Manager()
        a = A()
        b = B()
        c = C()

        x += a
        x += b
        x += c

        x.send(Event(), "*")
        self.assertFalse(a.flag)
        self.assertFalse(b.flag)
        self.assertTrue(c.flag)

        x -= a
        x -= b
        x -= c


    def testAllTargets(self):
        """Test All Targets

        Test that Events can be sent to all targets.
        """

        class A(Component):

            channel = "A"

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        class B(Component):

            channel = "B"

            flag = False

            @handler("bar")
            def onBAR(self, event, *args, **kwargs):
                self.flag = True

        class C(Component):

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        x = Manager()
        a = A()
        b = B()
        c = C()

        x += a
        x += b
        x += c

        x.send(Event(), "foo", "*")
        self.assertTrue(a.flag)
        self.assertFalse(b.flag)
        self.assertTrue(c.flag)

        x -= a
        x -= b
        x -= c


    def testAllTargetsAndChannels(self):
        """Test All Targets and Channels

        Test that Events can be sent to all channels on all targets.
        """

        class A(Component):

            channel = "A"

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        class B(Component):

            channel = "B"

            flag = False

            @handler("bar")
            def onBAR(self, event, *args, **kwargs):
                self.flag = True

        class C(Component):

            flag = False

            @handler("foo")
            def onFOO(self, event, *args, **kwargs):
                self.flag = True

        x = Manager()
        a = A()
        b = B()
        c = C()

        x += a
        x += b
        x += c

        x.send(Event(), "*", "*")
        self.assertTrue(a.flag)
        self.assertTrue(b.flag)
        self.assertTrue(c.flag)

        x -= a
        x -= b
        x -= c


    def testComponentAsManager(self):
        """Test Component

        Test that Components can manage their own events.
        """

        x = Manager()
        a = Foo()
        x += a
        a.push(Test(), "test")
        a.flush()
        self.assertTrue(a.flag)


    def testHandlerArgs(self):
        """Test Handler Args

        Test sending events to event handlers that accept positional arguments.
        """

        class A(Component):

            a = None
            b = None
            c = None

            varargs = None
            kwargs = None

            @handler("args")
            def onARGS(self, a, b, c):
                self.a = a
                self.b = b
                self.c = c

            @handler("varargs")
            def onVARARGS(self, *varargs):
                self.varargs = varargs

            @handler("kwargs")
            def onKWARGS(self, **kwargs):
                self.kwargs = kwargs

        x = Manager()
        a = A()
        x += a

        a.send(Test(1, 2, 3), "args")
        self.assertEquals(a.a, 1)
        self.assertEquals(a.b, 2)
        self.assertEquals(a.c, 3)

        a.send(Test(1, 2, 3), "varargs")
        self.assertEquals(a.varargs[0], 1)
        self.assertEquals(a.varargs[1], 2)
        self.assertEquals(a.varargs[2], 3)

        a.send(Test(a=1, b=2, c=3), "kwargs")
        self.assertEquals(a.kwargs["a"], 1)
        self.assertEquals(a.kwargs["b"], 2)
        self.assertEquals(a.kwargs["c"], 3)


    def testComponentLinks(self):
        """Test Component Links

        Test that components can be linked together and
        events can be sent to linked components.
        """

        foo = Foo()
        bar = Bar()
        foo + bar

        self.assertTrue(foo.onFOO in foo._handlers)
        self.assertTrue(bar.onBAR in foo._handlers)
        self.assertTrue(foo.onGOTBAR in foo._handlers)

        foo.send(Event(), "foo")
        self.assertTrue(foo.gotbar)

        foo - bar

        self.assertTrue(foo.onFOO in foo._handlers)
        self.assertTrue(bar.onBAR not in foo._handlers)
        self.assertTrue(foo.onGOTBAR in foo._handlers)

    def testEvent(self):
        """Test Event

        Test new Event construction and that it's associated
        arguments and keyword arguments are stored correctly.
        """

        e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

        self.assertEquals(e.name, "Test")
        self.assertEquals(e.channel, None)
        self.assertEquals(e.target, None)

        self.assertTrue((1, 2, 3, "foo", "bar") == e.args)

        self.assertEquals(e.kwargs["foo"], "1")
        self.assertEquals(e.kwargs["bar"], "2")

    def testEventRepr(self):
        """Test Event.__repr__

        Test Event's representation string.
        """

        e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

        self.assertEquals(repr(e),
                "<Test[] (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

        e.channel = "bar"
        self.assertEquals(repr(e),
                "<Test[bar] (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

        e.target = "foo"
        self.assertEquals(repr(e),
                "<Test[foo:bar] (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

    def testEventGetItem(self):
        """Test Event.__getitem__

        Test Event's multi attribute accessor.
        """

        e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

        self.assertEquals(e[0], 1)
        self.assertEquals(e[3], "foo")
        self.assertEquals(e["foo"], "1")

        try:
            e["???"]
            self.fail("Expected KeyError exception")
        except KeyError:
            pass

        try:
            e[True]
            self.fail("<type 'bool'> invalid for Event.__getitem__")
        except TypeError:
            pass


    def testEventEquality(self):
        """Test Event.__eq__

        Test Event equality.
        """

        a = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")
        b = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")
        self.assertEquals(a, b)

    def testManager(self):
        """Test Manager

        Test Manager construction. Test that the event queue is
        empty.
        """

        manager = Manager()
        self.assertEquals(len(manager), 0)
        self.assertEquals(len(manager._handlers), 0)

    def testManagerAddRemove(self):
        """Test Manager.add & Manager.remove

        Test that filters and listeners can be added to
        the global channel. Test that filters and listeners
        can be added to specific channels. Test that filters
        and listeners can be removed from all channels.
        Test that filters and listeners can be removed from
        a specific channel.
        """

        @handler("foo", filter=True)
        def onFOO():
            pass

        @handler("bar")
        def onBAR():
            pass

        def onTEST():
            pass

        manager = Manager()

        manager._add(onFOO)
        manager._add(onBAR)
        self.assertTrue(onFOO in manager.channels["*"])
        self.assertTrue(onBAR in manager.channels["*"])

        manager._add(onFOO, "foo")
        manager._add(onBAR, "bar")
        self.assertTrue(onFOO in manager.channels["foo"])
        self.assertTrue(onBAR in manager.channels["bar"])

        self.assertFalse(onTEST in manager.channels["*"])

        manager._remove(onFOO)
        self.assertTrue(onFOO not in manager._handlers)

        manager._remove(onBAR, "bar")
        self.assertTrue(onBAR not in manager.channels["bar"])
        self.assertTrue(onBAR in manager.channels["*"])
        manager._remove(onBAR)
        self.assertTrue(onBAR not in manager._handlers)

        self.assertEquals(len(manager._handlers), 0)

    def testManagerPushFlushSend(self):
        """Test Manager's push, flush and send

        Test that events can be pushed, fluahsed and that
        the event queue is empty after flushing. Test that
        events can be sent directly without queuing.

        Test that a filter will filter an event and prevent
        any further processing of this event.
        """

        import time

        self.flag = False
        self.foo = False

        @handler("test")
        def onTEST(test, time, stop=False):
            test.flag = True

        @handler("test")
        def onFOO(test, time, stop=False):
            test.foo = True

        @handler("bar")
        def onBAR(test, time):
            pass

        @handler(filter=True)
        def onSTOP(*args, **kwargs):
            return kwargs.get("stop", False)

        manager = Manager()

        manager._add(onSTOP)
        manager._add(onTEST, "test")
        manager._add(onFOO, "test")
        manager._add(onBAR, "bar")

        self.assertTrue(onSTOP in manager.channels["*"])
        self.assertTrue(onTEST in manager.channels["test"])
        self.assertTrue(onFOO in manager.channels["test"])
        self.assertTrue(onBAR in manager.channels["bar"])
        self.assertEquals(len(manager._handlers), 4)

        manager.push(Test(self, time.time()), "test")
        manager.flush()
        self.assertTrue(self.flag == True)
        self.flag = False
        self.assertTrue(self.foo == True)
        self.foo = False

        self.assertEquals(len(manager), 0)

        manager.send(Test(self, time.time()), "test")
        self.assertTrue(self.flag == True)
        self.flag = False

        manager.send(Test(self, time.time()), "test")
        self.assertTrue(self.flag == True)
        self.flag = False

        manager.send(Test(self, time.time(), stop=True), "test")
        self.assertTrue(self.flag == False)

        manager._remove(onSTOP)
        manager._remove(onTEST, "test")
        manager._remove(onFOO, "test")
        manager._remove(onBAR, "bar")

        self.assertEquals(len(manager._handlers), 0)


    def testHandlerTarget(self):
        """Test Handler Targets

        Test that event handlers can be registered with a custom
        target and that the event handler recieves the event
        even though it may be in a Component that defines a
        channel.
        """

        class Foo(Component):

            flag = False
            channel = "foo"

            @handler("foo")
            def onFOO(self):
                self.flag = True

        class Bar(Component):

            flag = False
            channel = "bar"

            @handler("foo", target="*")
            def onFOO2(self):
                self.flag = True

        class FooBar(Component):

            foo = False

            @handler("foo", target="*")
            def onFOO(self):
                self.foo = True

        manager = Manager()

        foo = Foo()
        bar = Bar()
        foobar = FooBar()

        manager += foo
        manager += bar
        manager += foobar

        manager.send(Event(), "foo", "foo")

        self.assertTrue(foo.flag)
        self.assertTrue(bar.flag)
        self.assertTrue(foobar.foo)

        foo.unregister()
        bar.unregister()
        foobar.unregister()

def suite():
    return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
    unittest.main()
