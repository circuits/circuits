# Module:	debugger
# Date:		2nd April 2006
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Debugger

Debugger component used to "debug"/"print" each event in a system.
"""

import sys

from circuits.core import listener, Component


class Debugger(Component):

	IgnoreEvents = []
	IgnoreChannels = []

	enabled = True

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
				print >> sys.stderr, event
