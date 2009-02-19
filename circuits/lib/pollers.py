# Module:	pollers
# Date:		15th September 2008
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Pollers

This module contains Poller components that enable polling of file or socket
descriptors for read/write events. Pollers:
 * Select
 * Poll
 * EPoll
 * KQueue
"""

try:
	from select26.select import select
except ImportError:
    from select import select

from circuits.core import Event, Component

TIMEOUT=0.00001

###
### Events
###

class Error(Event):
	"""Error(fd) -> Error Event

	Error Event fired when an error occurs on a file descriptor.
	"""

class Read(Event):
	"""Read(fd) -> Read Event

	Read Event fired when a file descriptor had data to be read.
	"""

class Write(Event):
	"""Write(fd) -> Write Event

	Write Event fired when a file descriptor is ready to be written to.
	"""

class Poller(Component):
	"""Poller(...) -> new Poller Component

	Creates a new Poller Component that can be used to poll file descriptors
	for read and write events. This is a base component and should be extended
	to implement the desired poller implementation.
	"""

	fds = []
	read = []
	write = []

	def add(self, fd):
		"""Poller.add(fd) -> None

		Add the given file descriptor fd to be polled.
		"""

		self.fds.append(fd)
		self.read.append(fd)
		self.write.append(fd)

	def remove(self, fd):
		"""Poller.remove(fd) -> None

		Remove the given file descriptor fd from being polled.
		"""

		self.fds.remove(fd)
		self.read.remove(fd)
		self.write.remove(fd)

	def poll(self, timeout=TIMEOUT):
		"""Poller.poll(timeout=TIMEOUT) -> None

		Base poll. Sub-classes should override this depending on the polling
		implementation.
		"""

		pass

class Select(Poller):
	"""Select(...) -> new Select Poller Component

	Creates a new Select Poller Component that uses the select poller
	implementation. This poller is not reccomneded but is available for legacy
	reasons as most systems implement select-based polling for backwards
	compatibility.
	"""

	def poll(self, timeout=TIMEOUT):
		r, w, e = select(self.read, self.write, self.fds, timeout)

		for fd in w:
			self.push(Write(fd), "write", self.channel)
			
		for fd in r:
			self.push(Read(fd), "read", self.channel)

		for fd in e:
			self.push(Error(fd), "error", self.channel)
