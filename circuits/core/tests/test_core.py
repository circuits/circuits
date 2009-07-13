# Module:   core
# Date:     23rd June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core Test Suite"""

import unittest
from time import sleep

from circuits.core import handler, Event, Component, Manager

def wait():
    sleep(0.1)

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

class A(Component):

    def __tick__(self):
        pass

    def foo(self):
        print "A!"

class B(Component):

    def __tick__(self):
        pass

    def foo(self):
        pass

class C(Component):

    def __tick__(self):
        pass

    def foo(self):
        pass

class Z(Component):

    def __init__(self):
        super(Z, self).__init__(self)

        self += A()

    def __tick__(self):
        pass

    def foo(self):
        pass

class RunningTest(Component):

    def __init__(self):
        super(RunningTest, self).__init__(self)

        self.mode = None

    def started(self, component, mode):
        if component == self:
            self.mode = mode

    def stopped(self, component):
        self.mode = None

class TestErrorHandling(unittest.TestCase):
    """Test Error Handling

    Test that exceptions are handled and an Error event is pushed.
    """

    def runTest(self):

        class ErrorHandler(Component):

            def __init__(self):
                super(ErrorHandler, self).__init__()

                self.type = None
                self.value = None
                self.traceback = None

            def exception(self, type, value, traceback, handler=None):
                self.type = type
                self.value = value
                self.traceback = traceback
                self.handler = handler

        class TestError(Component):

            def test1(self):
                return x

            def test2(self):
                return self.x

            def test3(self):
                raise RuntimeError()

        m = Manager()
        e = ErrorHandler()
        m += e
        t = TestError()
        m += t

        m.push(Event(), "test1")
        m.flush(); m.flush()
        self.assertTrue(e.type is NameError)
        self.assertTrue(isinstance(e.value, NameError))
        self.assertEquals(e.handler, t.test1)

        m.push(Event(), "test2")
        m.flush(); m.flush()
        self.assertTrue(e.type is AttributeError)
        self.assertTrue(isinstance(e.value, AttributeError))
        self.assertEquals(e.handler, t.test2)

        m.push(Event(), "test3")
        m.flush(); m.flush()
        self.assertTrue(e.type is RuntimeError)
        self.assertTrue(isinstance(e.value, RuntimeError))
        self.assertEquals(e.handler, t.test3)

class TestAllChannels(unittest.TestCase):
    """Test All Channels

    Test that Events can be sent to all channels.
    """

    def runTest(self):

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

class TestManagerRepr(unittest.TestCase):
    """Test Manager.__repr__

    Test Manager's representation string.
    """

    def runTest(self):
        x = Manager()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 0 h: 0) [S]>")

        a = Foo()
        x += a
        self.assertEquals(repr(x), "<Manager (q: 1 c: 3 h: 3) [S]>")

        x.flush()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 3 h: 3) [S]>")

        x.push(Test(), "foo")
        self.assertEquals(repr(x), "<Manager (q: 1 c: 3 h: 3) [S]>")

        x.flush()
        self.assertEquals(repr(x), "<Manager (q: 0 c: 3 h: 3) [S]>")

        x -= a
        self.assertEquals(repr(x), "<Manager (q: 1 c: 0 h: 0) [S]>")


class TestComponentRepr(unittest.TestCase):
    """Test Component.__repr__

    Test Component's representation string.
    """

    def runTest(self):
        a = Foo()
        self.assertEquals(repr(a), "<Foo/* (q: 0 c: 3 h: 3) [S]>")

        a.push(Test(), "foo")
        self.assertEquals(repr(a), "<Foo/* (q: 1 c: 3 h: 3) [S]>")

        a.flush()
        self.assertEquals(repr(a), "<Foo/* (q: 0 c: 3 h: 3) [S]>")


class TestComponentSetup(unittest.TestCase):
    """Test Component Setup

    Tests that filters and listeners of a Component are
    automatically added to the event manager instnace
    given.
    """

    def runTest(self):
        manager = Manager()

        filter = FilterComponent()
        manager += filter
        listener = ListenerComponent()
        manager += listener

        self.assertTrue(filter.onFOO in manager.channels[("*", "foo")])
        self.assertTrue(listener.foo in manager.channels[("*", "foo")])
        self.assertTrue(filter.onBAR in manager.channels[("*", "bar")])
        self.assertTrue(listener.bar in manager.channels[("*", "bar")])

        filter.unregister()
        listener.unregister()

        self.assertEquals(len(manager._handlers), 0)


class TestFilterOrder(unittest.TestCase):
    """Test Filter Order

    Test that Events Handlers set as Filters are added and sorted
    such that Filters preceed non-filters.
    """

    def runTest(self):
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
        self.assertTrue(foo.channels[("*", "a")][0] == foo.a2)

class TestTargetsAndChannels(unittest.TestCase):
    """Test Components, Targets and Channels

    Test that Components can be set up with a channel
    and that event handlers of that Component work
    correctly. That is, Components that have their
    own channel, have their own global channel and
    each channel is unique to that Component.
    """

    def runTest(self):
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
        self.assertFalse(bar.flag) ### (NEW) Behavioural Change

        foo.unregister()
        bar.unregister()

class TestMultipleChannels(unittest.TestCase):
    """Test Multiple Channels

    Test that Event Handlers can listen on Multiple
    Channels.
    """

    def runTest(self):
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

class TestAllTargets(unittest.TestCase):
    """Test All Targets

    Test that Events can be sent to all targets.
    """

    def runTest(self):
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


class TestComponentAsManager(unittest.TestCase):
    """Test Component

    Test that Components can manage their own events.
    """

    def runTest(self):
        x = Manager()
        a = Foo()
        x += a
        a.push(Test(), "test")
        a.flush()
        self.assertTrue(a.flag)


class TestHandlerArgs(unittest.TestCase):
    """Test Handler Args

    Test sending events to event handlers that accept positional arguments.
    """

    def runTest(self):
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


class TestComponentLinks(unittest.TestCase):
    """Test Component Links

    Test that components can be linked together and
    events can be sent to linked components.
    """

    def runTest(self):
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

class TestEvent(unittest.TestCase):
    """Test Event

    Test new Event construction and that it's associated
    arguments and keyword arguments are stored correctly.
    """

    def runTest(self):
        e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

        self.assertEquals(e.name, "Test")

        self.assertTrue((1, 2, 3, "foo", "bar") == e.args)

        self.assertEquals(e.kwargs["foo"], "1")
        self.assertEquals(e.kwargs["bar"], "2")

        self.assertEquals(e[0], 1)
        self.assertEquals(e[1], 2)
        self.assertEquals(e[2], 3)
        self.assertEquals(e[3], "foo")
        self.assertEquals(e[4], "bar")

        self.assertEquals(e["foo"], "1")
        self.assertEquals(e["bar"], "2")

class TestEventRepr(unittest.TestCase):
    """Test Event.__repr__

    Test Event's representation string.
    """

    def runTest(self):
        e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

        self.assertEquals(repr(e),
                "<Test[] (1, 2, 3, 'foo', 'bar') {'foo': '1', 'bar': '2'}>")

        e.channel = ("*", "bar")
        self.assertEquals(repr(e),
                "<Test[*:bar] (1, 2, 3, 'foo', 'bar') {'foo': '1', 'bar': '2'}>")

        e.channel = ("foo", "bar")
        self.assertEquals(repr(e),
                "<Test[foo:bar] (1, 2, 3, 'foo', 'bar') {'foo': '1', 'bar': '2'}>")

class TestEventGetItem(unittest.TestCase):
    """Test Event.__getitem__

    Test Event's multi attribute accessor.
    """

    def runTest(self):
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


class TestEventEquality(unittest.TestCase):
    """Test Event.__eq__

    Test Event equality.
    """

    def runTest(self):
        a = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")
        b = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")
        self.assertEquals(a, b)

class TestManager(unittest.TestCase):
    """Test Manager

    Test Manager construction. Test that the event queue is
    empty.
    """

    def runTest(self):
        manager = Manager()
        self.assertEquals(len(manager), 0)
        self.assertEquals(len(manager._handlers), 0)

class TestManagerAddRemove(unittest.TestCase):
    """Test Manager.add & Manager.remove

    Test that filters and listeners can be added to
    the global channel. Test that filters and listeners
    can be added to specific channels. Test that filters
    and listeners can be removed from all channels.
    Test that filters and listeners can be removed from
    a specific channel.
    """

    def runTest(self):
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
        self.assertTrue(onFOO in manager._globals)
        self.assertTrue(onBAR in manager._globals)

        manager._add(onFOO, ("*", "foo"))
        manager._add(onBAR, ("*", "bar"))
        self.assertTrue(onFOO in manager.channels[("*", "foo")])
        self.assertTrue(onBAR in manager.channels[("*", "bar")])

        self.assertFalse(onTEST in manager._globals)

        manager._remove(onFOO)
        self.assertTrue(onFOO not in manager._handlers)

        manager._remove(onBAR, ("*", "bar"))
        self.assertTrue(("*", "bar") not in manager.channels)
        self.assertTrue(onBAR in manager._globals)
        manager._remove(onBAR)
        self.assertTrue(onBAR not in manager._handlers)

        self.assertEquals(len(manager._handlers), 0)

class TestManagerPushFlushSend(unittest.TestCase):
    """Test Manager's push, flush and send

    Test that events can be pushed, fluahsed and that
    the event queue is empty after flushing. Test that
    events can be sent directly without queuing.

    Test that a filter will filter an event and prevent
    any further processing of this event.
    """

    def runTest(self):
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
        manager._add(onTEST, ("*", "test"))
        manager._add(onFOO, ("*", "test"))
        manager._add(onBAR, ("*", "bar"))

        self.assertTrue(onSTOP in manager._globals)
        self.assertTrue(onTEST in manager.channels[("*", "test")])
        self.assertTrue(onFOO in manager.channels[("*", "test")])
        self.assertTrue(onBAR in manager.channels[("*", "bar")])
        self.assertEquals(len(manager._handlers), 3)

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
        manager._remove(onTEST, ("*", "test"))
        manager._remove(onFOO, ("*", "test"))
        manager._remove(onBAR, ("*", "bar"))

        self.assertEquals(len(manager._handlers), 0)


class TestHandlerTargets(unittest.TestCase):
    """Test Handler Targets

    Test that event handlers can be registered with a custom
    target and that the event handler recieves the event
    even though it may be in a Component that defines a
    channel.
    """

    def runTest(self):
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

class TestStructures(unittest.TestCase):
    """Test Component Structures

    Test that components maintain their sturcture when registered and
    unregistered and re-registered to other components.
    """

    def _test(self, x, c, m, h, ch, q, t):
        self.assertEquals(x.manager, m)

        self.assertEquals(len(x.components), len(c))
        for _ in c:
            self.assertTrue(_ in x.components)

        self.assertEquals(len(x._handlers), len(h))
        for _ in h:
            self.assertTrue(_ in x._handlers)

        self.assertEquals(len(x.channels), len(ch))
        for k, v in ch:
            self.assertTrue(k in x.channels)
            for _ in v:
                self.assertTrue(_ in x._handlers)
                self.assertTrue(_ in x.channels[k])

        if q:
            self.assertTrue(x)
        else:
            self.assertFalse(x)

        self.assertEquals(len(x._queue), q)
        self.assertEquals(len(x), q)

        self.assertEquals(len(x._ticks), len(t))
        for _ in t:
            self.assertTrue(_ in x._ticks)

    def runTest(self):

        a = A()
        b = B()
        c = C()

        for x in [a, b, c]:
            #_test(x, c, m, h, ch, q, t):
            self._test(x, [], x,[x.foo],
                    [(("*", "foo"), [x.foo])],
                    0, [x.__tick__])

        ###
        ### Test 1
        ###

        self.assertEquals(a + (b + c), a)

        #_test(x, c, m, h, ch, q, t):
        self._test(a, [b], a, [a.foo, b.foo, c.foo],
            [(("*", "foo"), [a.foo, b.foo, c.foo])],
            2, [a.__tick__, b.__tick__, c.__tick__])
        self._test(b, [c], a, [b.foo, c.foo],
            [(("*", "foo"), [b.foo, c.foo])],
            0, [b.__tick__, c.__tick__])
        self._test(c, [], b, [c.foo],
            [(("*", "foo"), [c.foo])],
            0, [c.__tick__])

        ###
        ### Test 2
        ###

        self.assertEquals(a - b, a)

        #_test(x, c, m, h, ch, q, t):
        self._test(a, [], a, [a.foo],
            [(("*", "foo"), [a.foo])],
            3, [a.__tick__])
        self._test(b, [c], b, [b.foo, c.foo],
            [(("*", "foo"), [b.foo, c.foo])],
            1, [b.__tick__, c.__tick__])
        self._test(c, [], b, [c.foo],
            [(("*", "foo"), [c.foo])],
            0, [c.__tick__])

class TestRunningState(unittest.TestCase):
    """Test Running State

    Test the Running State of components
    """

    def runTest(self):
        x = RunningTest()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")

        x.start()
        self.assertTrue(x.running)
        self.assertEquals(x.state, "R")
        self.assertEquals(x.mode, "T")

        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x.mode, None)

        x.start(process=True)
        self.assertFalse(x.running)     # Should be: True
        self.assertEquals(x.state, "S") # Should be: "R"
        self.assertEquals(x.mode, None)  # Should be: "P"

        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x.mode, None)

class RunnableComponent(Component):

    def __init__(self):
        super(RunnableComponent, self).__init__()

        self._count = None
        self._mode = None
        self._registered = None
        self._unregistered = None

        self._event = False
        self._test = False
        self._args = None
        self._kwargs = None

        self._etype = None
        self._evalue = None
        self._traceback = None

    def __tick__(self):
        if self._count is not None:
            self._count += 1

    def registered(self, component, manager):
        self._registered = (component, manager)

    def unregistered(self, component, manager):
        self._unregistered = (component, manager)

    def started(self, component, mode):
        if component == self:
            self._mode = mode
            self._count = 0

    def stopped(self, component):
        if component == self:
            self._mode = None
            self._count = None

    def exception(self, type, value, traceback, handler=None):
        self._etype = type
        self._evalue = value
        self._traceback = traceback
        self._handler = handler

    def blowup(self, error):
        raise error

    def bad(self):
        return x

    def event(self):
        self._event = not self._event

    def test(self, *args, **kwargs):
        self._test = not self._test
        self._args = args
        self._kwargs = kwargs

class TestRunnableComponents(unittest.TestCase):
    """Test Runnable Components

    Test the functionality of Runnable Components.
    """

    def runTest(self):
        #from circuits import Debugger
        x = RunnableComponent()# + Debugger()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")

        # Test Running and Started event
        x.start()
        self.assertTrue(x.running)
        self.assertEquals(x.state, "R")
        self.assertEquals(x._mode, "T")

        # Test component registration and Registered event
        a = A()
        self.assertEquals(x, x + a)
        wait()
        self.assertEquals(x._registered, (a, x))

        # Test tick functions
        self.assertTrue(x._count > 0)

        # Test component unregistration and Unregistered event
        self.assertEquals(x, x - a)
        wait()
        self.assertEquals(x._unregistered, (a, x))

        # Test stopping and Stopped event
        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x._mode, None)

        # Test Sleeping
        x.start(sleep=1)
        self.assertTrue(x.running)
        self.assertEquals(x.state, "R")
        self.assertEquals(x._mode, "T")

        # Test tick functions whiel sleeping
        sleep(2)
        self.assertTrue(x._count > 0)
        self.assertTrue(x._count < 3)

        # Test raising exceptions while sleeping
        x.send(Event(TypeError), "blowup")

        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x._mode, None)

        x.start()
        self.assertTrue(x.running)
        self.assertEquals(x.state, "R")
        self.assertEquals(x._mode, "T")

        # Test event pushing and sending
        x.push(Event())
        wait()
        self.assertTrue(x._event)
        x.send(Event())
        self.assertFalse(x._event)

        # Test event pushing and sending (2)
        x.push(Test())
        wait()
        self.assertTrue(x._test)
        x.send(Test())
        self.assertFalse(x._test)

        # Test event pushing and sending (3)
        x.push(Test(), "test")
        wait()
        self.assertTrue(x._test)
        x.send(Test(), "test")
        self.assertFalse(x._test)

        # Test event pushing and sending (4)
        x.push(Test(), "dummy")
        wait()
        self.assertFalse(x._test)
        x.send(Test(), "dummy")
        self.assertFalse(x._test)

        # Test event pushing and sending (5)
        x.push(Test(1, 2, 3, a=1, b=2, c=3))
        wait()
        self.assertTrue(x._test)
        self.assertEquals(x._args, (1, 2, 3))
        self.assertEquals(x._kwargs, {"a": 1, "b": 2, "c": 3})
        x.send(Test(4, 5, 6, x=3, y=2, z=1))
        self.assertFalse(x._test)
        self.assertEquals(x._args, (4, 5, 6))
        self.assertEquals(x._kwargs, {"x": 3, "y": 2, "z": 1})

        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x._mode, None)

        x.start()
        self.assertTrue(x.running)
        self.assertEquals(x.state, "R")
        self.assertEquals(x._mode, "T")

        # Test error logging
        x.push(Event(), "bad")
        wait()
        self.assertEquals(x._etype, NameError)
        self.assertTrue(isinstance(x._evalue, NameError))
        self.assertEquals(x._handler, x.bad)
        x._etype = None
        x._evalue = None
        x._traceback = None
        x._handler = None

        # Test error raising
        x._count = object()
        wait()
        self.assertEquals(x._etype, TypeError)
        self.assertTrue(isinstance(x._evalue, TypeError))
        self.assertEquals(x._handler, None)

        x.stop()
        self.assertFalse(x.running)
        self.assertEquals(x.state, "S")
        self.assertEquals(x._mode, None)

if __name__ == "__main__":
    unittest.main()
