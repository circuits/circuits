# Module:	workers
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Workers

Worker components and managers.
"""

from threading import Thread
from threading import enumerate as threads

from circuits.core import Component


def workers():
	"""workers() -> list of workers

	Get the current list of active Worker's
	"""

	return [thread for thread in threads() if isinstance(thread, Worker)]


class Worker(Component, Thread):

	running = False

	def start(self):
		self.running = True
		super(Worker, self).start()

	def stop(self):
		self.running = False
