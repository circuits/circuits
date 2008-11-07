#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Simple Web Hello (WSGI)

Web-based Hello World example. This example is exactly the same as
the helloweb.py and simpleweb.py examples, except that this uses
a WSGI.
"""

from circuits.lib.web import Application, Controller

class HelloWorld(Controller):

	def index(self, *args, **kwargs):
		return "Hello World!"

application = Application()
application += HelloWorld()
