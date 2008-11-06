# Module:	web
# Date:		6th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Web Components

This module implements Web Components that can be used to build
web applications and web systems, be it an AJAX backend, a RESTful
server or a website. These components offer a full featured web
server implementation with support for headers, cookies, positional
and keyword arguments, filtering, url dispatching and more.
"""

from circuits.lib.sockets import TCPServer
from circuits.lib.http import HTTP, Dispatcher

class Server(TCPServer):

	def __init__(self, *args, **kwargs):
		super(Server, self).__init__(*args, **kwargs)

		self.manager += HTTP()
		self.manager += Dispatcher()

	def run(self):
		while True:
			try:
				self.flush()
				self.poll()
			except KeyboardInterrupt:
				break
