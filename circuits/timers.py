# Module:	timers
# Date:		04th August 2004
# Author:	James Mills <prologic@shortcircuit.net.au>

"""Timers

Timers component to facilitate timed eventd.
"""

from time import time

from circuits.core import Component


class Timer(Component):
	"""Timer(s, e, c, t, persist) -> new timer object

	Creates a new timer object which when triggered
	will return an event to be pushed onto the event
	queue held by the Timers component.
	"""

	def __init__(self, s, e, c="timer", t=None, persist=False):
		super(Timer, self).__init__()

		self.s = s
		self.e = e
		self.c = c
		self.t = t
		self.persist = persist

		self.reset()

	def reset(self):
		"""T.reset() -> None

		Reset the timer.
		"""

		self._eTime = time() + self.s

	def poll(self):
		"""T.poll() -> done, (e, c, t)

		Check if this timer is ready to be triggered.
		If so, return True, (e, c, t), otherwise
		return False, (None, None, None).

		If timer is persistent, reset it after triggering.
		"""

		if time() > self._eTime:
			self.push(self.e, self.c, self.t)

			if self.persist:
				self.reset()
			else:
				self.unregister()
				return True
