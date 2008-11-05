# Module:	bridge
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Bridge

Brige component to bridge one or more components in a single system.
That is, events in system A bridged to system B are shared. For exampe:

A <--> Bridge <--> B

Events that propagate in A, will propagate to B across the Bridge.
Events that propagate in B, will propagate to A across the Bridge.

When the Bridge is created, it will automatically attempt to send a
Helo event to any configured nodes. The default Bridge uses the UDP
as it's transmission protocol. Events thus cannot be guaranteed of
their order or delivery.
"""

import socket
import select
from cPickle import dumps as pickle
from cPickle import loads as unpickle
from socket import gethostname, gethostbyname, gethostbyaddr

from circuits.core import listener, Event, Component


__all__ = (
		"Bridge",
		)


POLL_INTERVAL = 0.00001
BUFFER_SIZE = 131072


class Read(Event): pass
class Helo(Event): pass
class Error(Event): pass
class Write(Event): pass
class Close(Event): pass


class Bridge(Component):

	IgnoreEvents = ["Read", "Write"]
	IgnoreChannels = []

	def __init__(self, port, address="", nodes=[], *args, **kwargs):
		super(Bridge, self).__init__(*args, **kwargs)

		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setsockopt(socket.SOL_SOCKET,	socket.SO_BROADCAST, 1)
		self._sock.setblocking(False)
		self._sock.bind((address, port))

		self._write = []
		self._buffers = {}
		self._read = [self._sock]

		self.address = address
		self.port = port

		self.nodes = set(nodes)

		if self.address in ["", "0.0.0.0"]:
			address = gethostbyname(gethostname())
		else:
			address = self.address

		self.ourself = (address, self.port)

	def registered(self):
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

		event.source = self.ourself
		s = pickle(event, -1)

		if self.nodes:
			for node in self.nodes:
				self.write(node, s)
		else:
			self.write(("<broadcast>", self.port), s)

	@listener("helo", type="filter")
	def onHELO(self, event, address, port):
		source = event.source

		if (address, port) == self.ourself or source in self.nodes:
			return True

		if not (address, port) in self.nodes:
			self.nodes.add((address, port))
			self.push(Helo(*self.ourself), "helo")

	@listener("read", type="filter")
	def onREAD(self, address, data):
		event = unpickle(data)

		channel = event.channel
		target = event.target
		source = event.source

		if source == self.ourself:
			return

		self.send(event, channel, target)

	def poll(self, wait=POLL_INTERVAL):
		r, w, e = select.select(self._read, self._write, [], wait)

		if w:
			for address, data in self._buffers.iteritems():
				if data:
					self.send(Write(address, data[0]), "write", self.channel)
			self._write.remove(w[0])

		if r:
			try:
				data, address = self._sock.recvfrom(BUFFER_SIZE)

				if not data:
					self.close()
				else:
					self.push(Read(address, data), "read", self.channel)
			except socket.error, e:
				self.push(Error(self._sock, e), "error", self.channel)
				self.close()

	def write(self, address, data):
		if not self._write:
			self._write.append(self._sock)
		if not self._buffers.has_key(address):
			self._buffers[address] = []
		self._buffers[address].append(data)

	def broadcast(self, data):
		self.write("<broadcast", data)

	def close(self):
		self.push(Close(), "close", self.channel)

	@listener("close", type="filter")
	def onCLOSE(self):
		"""Close Event

		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			self._read.remove(self._sock)
			self._write.remove(self._sock)
			self._sock.shutdown(2)
			self._sock.close()
		except socket.error, error:
			self.push(Error(error), "error", self.channel)

	@listener("write", type="filter")
	def onWRITE(self, address, data):
		"""Write Event


		Typically this should NOT be overridden by sub-classes.
		If it is, this should be called by the sub-class first.
		"""

		try:
			self._sock.sendto(data, address)
			del self._buffers[address][0]
		except socket.error, e:
			if e[0] in [32, 107]:
				self.close()
			else:
				self.push(Error(e), "error", self.channel)
				self.close()

