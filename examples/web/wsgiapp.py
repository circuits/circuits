#!/usr/bin/env python

from circuits.web import Application, Controller

class Root(Controller):

	def index(self):
		return "Hello World!"

application = Application() + Root()
