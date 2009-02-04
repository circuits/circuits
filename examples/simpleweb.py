#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Simple Web Hello

Web-based Hello World example. This example is exactly the same as
the helloweb.py example, except that it tries to simplify things by
using more higher abstracted web components from the web components
library.
"""

#import hotshot
#import hotshot.stats

import psyco; psyco.full()

from circuits.web import Server, Controller

class HelloWorld(Controller):

	def index(self):
		return "Hello World!"

#profiler = hotshot.Profile("simpleweb.prof")
#profiler.start()

server = Server(8000)
server += HelloWorld()
server.run()

#profiler.stop()
#profiler.close()
#stats = hotshot.stats.load("simpleweb.prof")
#stats.strip_dirs()
#stats.sort_stats("time", "calls")
#stats.print_stats(20)
