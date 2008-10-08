# Module:	bridge
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Bridge

Brige component to bridge one or more other nodes in a single system.
That is, events in system A bridged to system B are shared. For exampe:

A <--> Bridge <--> B

Events that propagate in A, will propagate to B across the Bridge.
Events that propagate in B, will propagate to A across the Bridge.

When the Bridge is created, it will automatically attempt to send a
Helo event to any configured nodes.
"""

from cPickle import dumps as pickle
from cPickle import loads as unpickle
from socket import gethostname, gethostbyname, gethostbyaddr

from circuits.core import listener, Event


class Helo(Event):
	pass


class DummyBridge(object):

	def poll(self, *args, **kwargs):
		pass


class Bridge(UDPServer):

	IgnoreEvents = ["Read", "Write"]
	IgnoreChannels = []

	def __init__(self, *args, **kwargs):
		super(Bridge, self).__init__(*args, **kwargs)

		self.nodes = set(kwargs.get("nodes", []))

		if self.address in ["", "0.0.0.0"]:
			address = gethostbyname(gethostname())
		else:
			address = self.address

		self.ourself = (address, self.port)

		self.push(Helo(*self.ourself), "helo")

	@listener(type="filter")
	def onEVENTS(self, event, *args, **kwargs):
		channel = event.channel
		if True in [event.name == name for name in self.IgnoreEvents]:
			return
		elif channel in self.IgnoreChannels:
			return
		elif event.ignore:
			return
		else:
			event.ignore = True

		s = pickle(event, -1)
		if self.nodes:
			for node in self.nodes:
				self.write(node, s)
		else:
			self.write(("<broadcast>", self.port), s)

	@filter("pong")
	def onHELO(self, event, address, port, time):
		print "PONG: %s" % event

	@filter("helo")
	def onHELO(self, event, address, port):
		source = event.source

		if (address, port) == self.ourself or source in self.nodes:
			return True

		if not (address, port) in self.nodes:
			self.nodes.add((address, port))
			self.push(Helo(*self.ourself), "helo")

	@filter("read")
	def onREAD(self, address, data):
		event = unpickle(data)
		channel = event.channel
		target = event.target
		source = event.source
		if not source:
			event.source = address
		self.send(event, channel, target)
