# Module:	event
# Date:		23rd June 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Core Test Suite

Test all functionality of the event library.
"""

import unittest

import circuits
from circuits import *
from circuits.core import InvalidHandler

class Test(Event):
	"""Test(Event) -> Test Event"""

class FilterComponent(Component):

	@filter("foo")
	def onFOO(self, msg=""):
		return True

	@filter("bar")
	def onBAR(self, msg=""):
		if msg.lower() == "hello world":
			return True

class ListenerComponent(Component):

	@listener("foo")
	def onFOO(self, test, msg=""):
		if msg.lower() == "start":
			self.push(Test(msg="foo"), "foo")

	@listener("bar")
	def onBAR(self, test, msg=""):
		if msg.lower() == "test":
			self.push(Test(msg="hello world"), event._channel)

class Foo(Component):

	gotbar = False

	@listener("foo")
	def onFOO(self, event):
		return self.send(Test(), "bar")

	@listener("gotbar")
	def onGOTBAR(self, event, *args):
		self.gotbar = True
		return "gotbar"

class Bar(Component):

	@listener("bar")
	def onBAR(self, event, *args, **kwargs):
		return self.send(Test(), "gotbar")

class EventTestCase(unittest.TestCase):

	def testManagerRepr(self):
		"""Test Manager.__repr__

		Test Manager's representation string.
		"""

		x = Manager()
		self.assertEquals(repr(x), "<Manager (q: 0 h: 0)>")

		a = Foo()
		x += a
		self.assertEquals(repr(x), "<Manager (q: 1 h: 2)>")

		x.flush()
		self.assertEquals(repr(x), "<Manager (q: 0 h: 2)>")

		x.push(Test(), "foo")
		self.assertEquals(repr(x), "<Manager (q: 1 h: 2)>")

		x.flush()
		self.assertEquals(repr(x), "<Manager (q: 0 h: 2)>")

		x -= a
		self.assertEquals(repr(x), "<Manager (q: 0 h: 0)>")


	def testComponentRepr(self):
		"""Test Component.__repr__

		Test Component's representation string.
		"""

		a = Foo()
		self.assertEquals(repr(a), "<Foo/ component (q: 0 h: 2)>")

		a.push(Test(), "foo")
		self.assertEquals(repr(a), "<Foo/ component (q: 1 h: 2)>")

		a.flush()
		self.assertEquals(repr(a), "<Foo/ component (q: 0 h: 2)>")


	def testComponentSetup(self):
		"""Test Component Setup

		Tests that filters and listeners of a Component are
		automatically added to the event manager instnace
		given.
		"""

		filter = FilterComponent()
		circuits.manager += filter
		listener = ListenerComponent()
		circuits.manager += listener

		self.assertTrue(filter.onFOO in circuits.manager["foo"])
		self.assertTrue(listener.onFOO in circuits.manager["foo"])
		self.assertTrue(filter.onBAR in circuits.manager["bar"])
		self.assertTrue(listener.onBAR in circuits.manager["bar"])

		filter.unregister()
		listener.unregister()

		self.assertEquals(len(circuits.manager._handlers), 0)


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

			@filter()
			def onALL(self, event, *args, **kwargs):
				self.flag = True
				return True

			@listener("foo")
			def onFOO(self):
				self.flag = False

		class Bar(Component):

			flag = False

			@listener("bar")
			def onBAR(self):
				self.flag = True

		foo = Foo()
		bar = Bar()
		circuits.manager += foo
		circuits.manager += bar

		circuits.manager.send(Event(), "foo", foo.channel)
		self.assertTrue(foo.flag)
		circuits.manager.send(Event(), "bar")
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

			@listener("foo", "bar")
			def onFOOBAR(self, event, *args, **kwargs):
				self.flag = True

		foo = Foo()
		circuits.manager += foo

		circuits.manager.send(Event(), "foo")
		self.assertTrue(foo.flag)
		foo.flag = False

		circuits.manager.send(Event(), "bar")
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

			@listener("foo")
			def onFOO(self, event, *args, **kwargs):
				self.flag = True

		class B(Component):

			channel = "B"

			flag = False

			@listener("foo")
			def onFOO(self, event, *args, **kwargs):
				self.flag = True

		class C(Component):

			flag = False

			@listener("foo")
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

			@listener("foo")
			def onFOO(self, event, *args, **kwargs):
				self.flag = True

		class B(Component):

			channel = "B"

			flag = False

			@listener("bar")
			def onBAR(self, event, *args, **kwargs):
				self.flag = True

		class C(Component):

			flag = False

			@listener("foo")
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

			@listener("foo")
			def onFOO(self, event, *args, **kwargs):
				self.flag = True

		class B(Component):

			channel = "B"

			flag = False

			@listener("bar")
			def onBAR(self, event, *args, **kwargs):
				self.flag = True

		class C(Component):

			flag = False

			@listener("foo")
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

		self.assertEquals(e.__class__.__bases__, (object,))
		self.assertEquals(e.name, "Test")
		self.assertEquals(e.channel, None)
		self.assertEquals(e.target, None)
		self.assertFalse(e.ignore)

		self.assertTrue((1, 2, 3, "foo", "bar") == e.args)

		self.assertEquals(e.kwargs["foo"], "1")
		self.assertEquals(e.kwargs["bar"], "2")

	def testEventRepr(self):
		"""Test Event.__repr__

		Test Event's representation string.
		"""

		e = Test(1, 2, 3, "foo", "bar", foo="1", bar="2")

		self.assertEquals(repr(e),
				"<Test/ (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

		e.channel = "bar"
		self.assertEquals(repr(e),
				"<Test/bar (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

		e.target = "foo"
		self.assertEquals(repr(e),
				"<Test/foo:bar (1, 2, 3, 'foo', 'bar', foo=1, bar=2)>")

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

		self.assertEquals(len(circuits.manager), 2)
		self.assertEquals(len(circuits.manager._handlers), 0)

	def testManagerAddRemove(self):
		"""Test Manager.add & Manager.remove

		Test that filters and listeners can be added to
		the global channel. Test that filters and listeners
		can be added to specific channels. Test that
		non-filters and non-listeners cannot be added to any
		channel and raises an InvalidHandler. Test that filters
		and listeners can be removed from all channels.
		Test that filters and listeners can be removed from
		a specific channel.
		"""

		@filter("foo")
		def onFOO():
			pass

		@listener("bar")
		def onBAR():
			pass

		def onTEST():
			pass

		circuits.manager.add(onFOO)
		circuits.manager.add(onBAR)
		self.assertTrue(onFOO in circuits.manager.channels["*"])
		self.assertTrue(onBAR in circuits.manager.channels["*"])

		circuits.manager.add(onFOO, "foo")
		circuits.manager.add(onBAR, "bar")
		self.assertTrue(onFOO in circuits.manager["foo"])
		self.assertTrue(onBAR in circuits.manager["bar"])

		try:
			circuits.manager.add(onTEST)
		except InvalidHandler, error:
			pass

		self.assertFalse(onTEST in circuits.manager.channels["*"])

		circuits.manager.remove(onFOO)
		self.assertTrue(onFOO not in circuits.manager._handlers)

		circuits.manager.remove(onBAR, "bar")
		self.assertTrue(onBAR not in circuits.manager["bar"])
		self.assertTrue(onBAR in circuits.manager.channels["*"])
		circuits.manager.remove(onBAR)
		self.assertTrue(onBAR not in circuits.manager._handlers)

		self.assertEquals(len(circuits.manager._handlers), 0)

	def testManagerPushFlushSend(self):
		"""Test Manager's push, flush and send

		Test that events can be pushed, fluahsed and that
		the event queue is empty after flushing. Test that
		events can be sent directly without queuing.

		Test that Event._channel, Event._time and
		Event._source are set appropiately.

		Test that a filter will filter an event and prevent
		any further processing of this event.
		"""

		import time

		self.flag = False
		self.foo = False

		@listener("test")
		def onTEST(test, time, stop=False):
			test.flag = True

		@listener("test")
		def onFOO(test, time, stop=False):
			test.foo = True

		@listener("bar")
		def onBAR(test, time):
			pass

		@filter()
		def onSTOP(*args, **kwargs):
			return kwargs.get("stop", False)

		circuits.manager.add(onSTOP)
		circuits.manager.add(onTEST, "test")
		circuits.manager.add(onFOO, "test")
		circuits.manager.add(onBAR, "bar")

		self.assertTrue(onSTOP in circuits.manager.channels["*"])
		self.assertTrue(onTEST in circuits.manager["test"])
		self.assertTrue(onFOO in circuits.manager["test"])
		self.assertTrue(onBAR in circuits.manager["bar"])
		self.assertEquals(len(circuits.manager._handlers), 4)

		circuits.manager.push(Test(self, time.time()), "test")
		circuits.manager.flush()
		self.assertTrue(self.flag == True)
		self.flag = False
		self.assertTrue(self.foo == True)
		self.foo = False

		self.assertEquals(len(circuits.manager), 0)

		circuits.manager.send(Test(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		circuits.manager.send(Test(self, time.time()), "test")
		self.assertTrue(self.flag == True)
		self.flag = False

		circuits.manager.send(Test(self, time.time(), stop=True), "test")
		self.assertTrue(self.flag == False)

		circuits.manager.remove(onSTOP)
		circuits.manager.remove(onTEST, "test")
		circuits.manager.remove(onFOO, "test")
		circuits.manager.remove(onBAR, "bar")

		self.assertEquals(len(circuits.manager._handlers), 0)

def suite():
	return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
	unittest.main()
