# Module:	core
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Core

Core components and managers.
"""

from itertools import chain
from collections import deque
from collections import defaultdict
from inspect import getargspec, getmembers


class Error(Exception):
	pass

class InvalidHandler(Error):
	"""InvalidHandler(handler) -> Invalid Handler Exception

	Invalid Handler Exception raised when adding a function
	to a manager that is neither a listener or filter.
	"""

	def __init__(self, handler):
		super(InvalidHandler, self).__init__()
		self.handler = handler

class Event(object):
	"""Event(*args, **kwargs) -> new event object

	Create a new event object populating it with the given
	list of arguments and dictionary of keyword arguments.
	"""

	channel = None
	target = None

	source = None # Used by Bridge
	ignore = False # Used by Bridge

	def __new__(cls, *args, **kwargs):
		self = object.__new__(Event)
		self.name = cls.__name__
		self.args = args
		self.kwargs = kwargs
		return self

	def __eq__(self, y):
		" x.__eq__(y) <==> x==y"

		attrs = ["name", "args", "kwargs", "channel", "target"]
		r = [getattr(self, a) == getattr(y, a) for a in attrs]
		return False not in r

	def __repr__(self):
		"x.__repr__() <==> repr(x)"

		if self.channel is not None and self.target is not None:
			channelStr = "%s:%s" % (self.target, self.channel)
		elif self.channel is not None:
			channelStr = self.channel
		else:
			channelStr = ""
		argsStr = ", ".join([("%s" % repr(arg)) for arg in self.args])
		kwargsStr = ", ".join(
				[("%s=%s" % kwarg) for kwarg in self.kwargs.iteritems()])
		return "<%s/%s (%s, %s)>" % (self.name, channelStr, argsStr, kwargsStr)

	def __getitem__(self, x):
		"x.__getitem__(y) <==> x[y]"

		if type(x) == int:
			return self.args[x]
		elif type(x) == str:
			return self.kwargs[x]
		else:
			raise TypeError("Expected int or str, got %r" % type(x))


def listener(*args, **kwargs):
	"""listener(*args, **kwargs) -> new listener handler

	Decorator to wrap a function into an event handler that
	listens on a set of channels defined by args. The type
	of the listener defaults to "listener" and is defined
	by kwargs["type"]. To define a filter, pass type="filter"
	to kwargs.
	"""

	def decorate(f):
		f.type = kwargs.get("type", "listener")
		f.channels = args
		f.argspec = getargspec(f)
		f.args = f.argspec[0]
		f.varargs = (True if f.argspec[1] else False)
		f.varkw = (True if f.argspec[2] else False)
		if f.args and f.args[0] == "self":
			del f.args[0]
		return f
	return decorate


class Registered(Event):
	"""Registered(Event) -> Registered Event"""


class Manager(object):
	"""Manager() -> new event manager

	Create a new event manager which manages events.
	"""

	def __init__(self, *args, **kwargs):
		super(Manager, self).__init__()

		self._queue = deque()

		self._handlers = set()

		self.manager = self
		self.channels = defaultdict(list)

	def __repr__(self):
		q = len(self._queue)
		h = len(self._handlers)
		return "<Manager (q: %d h: %d)>" % (q, h)

	def __getitem__(self, x):
		return self.channels[x]

	def __len__(self):
		return len(self._queue)

	def __add__(self, y):
		y.register(self.manager)
		return self
	
	def __iadd__(self, y):
		y.register(self.manager)
		return self

	def __sub__(self, y):
		y.unregister()
		return self

	def handlers(self, s):
		channels = self.channels

		if ":" in s:
			target, channel = s.split(":", 1)
		else:
			channel = s
			target = None

		globals = channels["*"]

		if target == "*" and channel == "*":
			return self._handlers
		else:
			if target == "*":
				c = ":%s" % channel
				x = [channels[k] for k in channels if k == channel or k.endswith(c)]
				all = [i for y in x for i in y]
				return chain(globals, all)
			elif channel == "*":
				c = "%s:" % target
				x = [channels[k] for k in channels if k.startswith(c) or ":" not in k]
				all = [i for y in x for i in y]
				return chain(globals, all)
			else:
				all = channels["%s:*" % target]
				return chain(globals, all, channels[s])


	def add(self, handler, channel=None):
		"""E.add(handler, channel) -> None

		Add a new filter or listener to the event manager
		adding it to the given channel. If no channel is
		given, add it to the global channel.
		"""

		if getattr(handler, "type", None) not in ["filter", "listener"]:
			raise InvalidHandler(handler)

		self._handlers.add(handler)

		if channel is None:
			channel = "*"

		if channel in self.channels:
			if handler not in self.channels[channel]:
				self.channels[channel].append(handler)
				self.channels[channel].sort(key=lambda x: x.type)
		else:
			self.channels[channel] = [handler]

	def remove(self, handler, channel=None):
		"""E.remove(handler, channel=None) -> None

		Remove the given filter or listener from the
		event manager removing it from the given channel.
		if channel is None, remove it from the global
		channel. This will succeed even if the specified
		handler has already been removed.
		"""

		if channel is None:
			if handler in self.channels["*"]:
				self.channels["*"].remove(handler)
			keys = self.channels.keys()
		else:
			keys = [channel]

		if handler in self._handlers:
			self._handlers.remove(handler)

		for channel in keys:
			if handler in self.channels[channel]:
				self.channels[channel].remove(handler)


	def push(self, event, channel, target=None):
		"""E.push(event, channel, target=None) -> None

		Push the given event onto the given channel.
		This will queue the event up to be processed later
		by flushEvents. If target is given, the event will
		be queued for processing by the component given by
		target.
		"""

		if self.manager == self:
			event.channel = channel
			event.target = target
			self._queue.append(event)
		else:
			self.manager.push(event, channel, target)

	def flush(self):
		"""E.flushEvents() -> None

		Flush all events waiting in the queue.
		Any event waiting in the queue will be sent out
		to filters/listeners.
		"""

		if self.manager == self:
			q = self._queue
			self._queue = deque()
			while q:
				event = q.pop()
				channel = event.channel
				target = event.target
				self.send(event, channel, target)
		else:
			self.manager.flush()

	def send(self, event, channel, target=None):
		"""E.send(event, channel, target=None) -> None

		Send the given event to filters/listeners on the
		channel specified. If target is given, send this
		event to filters/listeners of the given target
		component.
		"""

		if self.manager == self:
			event.channel = channel
			event.target = target
			eargs = event.args
			ekwargs = event.kwargs
			if target is not None:
				channel = "%s:%s" % (target, channel)

			filter = False
			handler = None
			for handler in self.handlers(channel):
				args = handler.args
				varargs = handler.varargs
				varkw = handler.varkw

				if args and args[0] == "event":
					filter = handler(event, *eargs, **ekwargs)
				elif args:
					filter = handler(*eargs, **ekwargs)
				else:
					if varargs and varkw:
						filter = handler(*eargs, **ekwargs)
					elif varkw:
						filter = handler(**ekwargs)
					elif varargs:
						filter = handler(*eargs)
					else:
						filter = handler()

				if filter and handler.type == "filter":
					break
		else:
			self.manager.send(event, channel, target)


class Component(Manager):
	"""Component() -> new component object

	This should be sub-classed with methods defined for filters
	and listeners. Only one instance of any component can be
	instantiated. Further instantiation of the same component
	results in the same instance previously instantiated.

	Any filter/listeners found in the class will automatically
	be setup and added to the event manager. If a channel is
	requireed one will be added.

	Filters and Listeners are defined like so:

	C{
	@filter()
	def onFOO(self):
		return True

	@listener()
	def onBAR(self):
		print event
	}
	"""

	channel = None

	def __init__(self, *args, **kwargs):
		super(Component, self).__init__(*args, **kwargs)

		self.channel = kwargs.get("channel", self.channel)
		self.register(self)


	def __repr__(self):
		name = self.__class__.__name__
		channel = self.channel or ""
		q = len(self._queue)
		h = len(self._handlers)
		return "<%s/%s component (q: %d h: %d)>" % (name, channel, q, h)

	def register(self, manager):
		handlers = [x[1] for x in getmembers(self) if callable(x[1]) and
				hasattr(x[1], "type")]

		for handler in handlers:
			if handler.channels:
				channels = handler.channels
			else:
				channels = ["*"]

			for channel in channels:
				if self.channel is not None:
					channel = "%s:%s" % (self.channel, channel)

				manager.add(handler, channel)

		if not manager == self:
			manager.push(Registered(), "registered", self.channel)

		self.manager = manager


	def unregister(self):
		"""C.unregister() -> None

		Unregister all listeners/filters associated with
		this component
		"""

		for handler in self._handlers.copy():
			self.manager.remove(handler)

		self.manager = self
