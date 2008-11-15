#!/usr/bin/env python

import os
import sys
import os.path

from circuits.lib.web import Filter
from circuits.lib.web import Middleware
from circuits.lib.web import Application
from circuits.lib.web import Server, Logger, Controller

class Debug(object):

	tpl = """\
<html>
<head>
 <title>WSGI Debug</title>
</head>
<body>
 <h1>WSGI Debug</h1>
 <table border=1>
  <tr><th colspan=2>1. System Information</th></tr>
  <tr><td>Python</td><td>%(python_version)s</td></tr>
  <tr><td>Python Path</td><td>%(python_path)s</td></tr>
  <tr><td>Platform</td><td>%(platform)s</td></tr>
  <tr><td>Absolute path of this script</td><td>%(abs_path)s</td></tr>
  <tr><td>Filename</td><td>%(filename)s</td></tr>
  <tr><th colspan=2>2. WSGI Environment</th></tr>
%(wsgi_env)s
 </table>
</body>
</html>"""

	rowtpl = "  <tr><td>%s</td><td>%r</td></tr>"

	def __call__(self, environ, start_response):
		status = "200 OK"
		headers = [("Content-Type", "text/html"), ]
		start_response(status, headers)

		content = self.tpl % {
			"python_version": sys.version,
			"platform": sys.platform,
			"abs_path": os.path.abspath("."),
			"filename": __file__,
			"python_path": repr(sys.path),
			"wsgi_env": "\n".join([self.rowtpl % item for item in environ.items()]),
		}

		return [content]

def foo(environ, start_response):
	status = "200 OK"
	response_headers = [("Content-type", "text/plain")]
	start_response(status, response_headers)
	return ["foo"]

class Capitalizer(object):
	"Capitalizer Middleware"

	def __init__(self, app):
		self.app = app

	def __call__(self, environ, start_response):
		r = self.app(environ, start_response)
		s = "".join(r)
		return [s.upper()]

class CapitalizerFilter(Filter):
	"Capitalizer Filter"

	def process(self):
		return self.response.body.upper()

class Hello(Application):
	"Hello Application"

	channel = "/hello"

	def index(self):
		return "Hello from Hello"

class Root(Controller):
	"Root Controller"

	def index(self):
		return "Hello from Root"

server = Server(8000)
#server += Logger()
server += Hello()
server += Root()

#server += Middleware(foo) # <-- Not so useful :/
server += Middleware(foo, "/foo") # Mounts foo to /foo
server += Middleware(Debug(), "/debug") # Mounts Debug() to /debug
server += CapitalizerFilter()

for c in server.channels:
	print "%s" % c
	for h in server.channels[c]:
		print " %s" % h

server.run()
