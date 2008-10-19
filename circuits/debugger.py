# Module:	debugger
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Debugger

Debugger component used to "debug"/"print" each event in a system.
"""

import sys

from circuits.core import listener, Event, Component


class Debug(Event):
	"""Debug(Event) -> Debug Log Event

	args: msg
	"""


class Debugger(Component):

	IgnoreEvents = []
	IgnoreChannels = []

	enabled = True

	def __init__(self, *args, **kwargs):
		super(Debugger, self).__init__(*args, **kwargs)

		self.log = kwargs.get("log", None)

	def disable(self):
		self.enabled = False

	def enable(self):
		self.enabled = True

	def toggle(self):
		if self.enabled:
			self.disable()
		else:
			self.enable()

	def set(self, flag):
		if (not self.enabled) and flag:
			self.enable()
		elif self.enabled and (not flag):
			self.disable()

	@listener(type="filter")
	def onEVENTS(self, event, *args, **kwargs):
		if self.enabled:
			channel = event.channel
			if True in [event.name == name for name in self.IgnoreEvents]:
				return
			elif channel in self.IgnoreChannels:
				return
			else:
				if self.log:
					if isinstance(self.log, logging.Logger)
						self.log.debug(event)
					else:
						self.push(Debug(repr(event)), "debug", "log")
				else:
					print >> sys.stderr, event
