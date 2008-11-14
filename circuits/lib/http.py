# Module:	http
# Date:		13th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Hyper Text Transfer Protocol

This module implements the Hyper Text Transfer Protocol
or commonly known as HTTP.
"""

import re
import os
import cgi
import sys
import stat
import time
import gzip
import zlib
import struct
import cStringIO
from urllib import unquote
from urlparse import urlparse
from cStringIO import StringIO
from time import time, strftime
from Cookie import SimpleCookie
from traceback import format_exc
from types import ListType, TupleType

try:
	import cherrypy
	from cherrypy.lib.caching import expires
	from cherrypy.lib.static import serve_file
	from cherrypy._cpcgifs import FieldStorage
	from cherrypy import HTTPError, NotFound, HTTPRedirect
except ImportError:
	cherrypy = None

import circuits
from circuits.core import listener, Event, Component

###
### Header Support
###


# Regular expression that matches `special' characters in parameters, the
# existance of which force quoting of the parameter value.

tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')
q_separator = re.compile(r'; *q *=')

def _formatparam(param, value=None, quote=1):
	"""Convenience function to format and return a key=value pair.

	This will quote the value if needed or if quote is true.
	"""
	if value is not None and len(value) > 0:
		if quote or tspecials.search(value):
			value = value.replace('\\', '\\\\').replace('"', r'\"')
			return '%s="%s"' % (param, value)
		else:
			return '%s=%s' % (param, value)
	else:
		return param

def header_elements(fieldname, fieldvalue):
	"""Return a HeaderElement list from a comma-separated header str."""
	
	if not fieldvalue:
		return None
	headername = fieldname.lower()
	
	result = []
	for element in fieldvalue.split(","):
		if headername.startswith("accept") or headername == 'te':
			hv = AcceptElement.from_str(element)
		else:
			hv = HeaderElement.from_str(element)
		result.append(hv)
	
	result.sort()
	return result

class HeaderElement(object):
	"""An element (with parameters) from an HTTP header's element list."""
	
	def __init__(self, value, params=None):
		self.value = value
		if params is None:
			params = {}
		self.params = params
	
	def __unicode__(self):
		p = [";%s=%s" % (k, v) for k, v in self.params.iteritems()]
		return u"%s%s" % (self.value, "".join(p))
	
	def __str__(self):
		return str(self.__unicode__())
	
	def parse(elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in elementstr.split(";") if x.strip()]
		initial_value = atoms.pop(0).strip()
		params = {}
		for atom in atoms:
			atom = [x.strip() for x in atom.split("=", 1) if x.strip()]
			key = atom.pop(0)
			if atom:
				val = atom[0]
			else:
				val = ""
			params[key] = val
		return initial_value, params
	parse = staticmethod(parse)
	
	def from_str(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parse(elementstr)
		return cls(ival, params)
	from_str = classmethod(from_str)

class AcceptElement(HeaderElement):
	"""An element (with parameters) from an Accept* header's element list.
	
	AcceptElement objects are comparable; the more-preferred object will be
	"less than" the less-preferred object. They are also therefore sortable;
	if you sort a list of AcceptElement objects, they will be listed in
	priority order; the most preferred value will be first. Yes, it should
	have been the other way around, but it's too late to fix now.
	"""
	
	def from_str(cls, elementstr):
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = q_separator.split(elementstr, 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.from_str(atoms[0].strip())
		
		media_type, params = cls.parse(media_range)
		if qvalue is not None:
			params["q"] = qvalue
		return cls(media_type, params)
	from_str = classmethod(from_str)
	
	def qvalue(self):
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		return float(val)
	qvalue = property(qvalue, doc="The qvalue, or priority, of this value.")
	
	def __cmp__(self, other):
		diff = cmp(other.qvalue, self.qvalue)
		if diff == 0:
			diff = cmp(str(other), str(self))
		return diff

class Headers(dict):
	"""Manage a collection of HTTP response headers"""

	def __init__(self, headers=[]):
		if type(headers) is not ListType:
			raise TypeError("Headers must be a list of name/value tuples")
		self._headers = headers

	def __len__(self):
		"""Return the total number of headers, including duplicates."""
		return len(self._headers)

	def __setitem__(self, name, val):
		"""Set the value of a header."""
		del self[name]
		self._headers.append((name, val))

	def __delitem__(self,name):
		"""Delete all occurrences of a header, if present.

		Does *not* raise an exception if the header is missing.
		"""
		name = name.lower()
		self._headers[:] = [kv for kv in self._headers if kv[0].lower()<>name]

	def __getitem__(self,name):
		"""Get the first header value for 'name'

		Return None if the header is missing instead of raising an exception.

		Note that if the header appeared multiple times, the first exactly which
		occurrance gets returned is undefined. Use getall() to get all
		the values matching a header field name.
		"""
		return self.get(name)

	def pop(self, name, default=None):
		value = self.get(name, default)
		del self[name]
		return value

	def has_key(self, name):
		"""Return true if the message contains the header."""
		return self.get(name) is not None

	__contains__ = has_key

	def get_all(self, name):
		"""Return a list of all the values for the named field.

		These will be sorted in the order they appeared in the original header
		list or were added to this instance, and may contain duplicates. Any
		fields deleted and re-inserted are always appended to the header list.
		If no fields exist with the given name, returns an empty list.
		"""
		name = name.lower()
		return [kv[1] for kv in self._headers if kv[0].lower()==name]

	def get(self,name,default=None):
		"""Get the first header value for 'name', or return 'default'"""
		name = name.lower()
		for k,v in self._headers:
			if k.lower()==name:
				return v
		return default

	def keys(self):
		"""Return a list of all the header field names.

		These will be sorted in the order they appeared in the original header
		list, or were added to this instance, and may contain duplicates.
		Any fields deleted and re-inserted are always appended to the header
		list.
		"""
		return [k for k, v in self._headers]

	def values(self):
		"""Return a list of all header values.

		These will be sorted in the order they appeared in the original header
		list, or were added to this instance, and may contain duplicates.
		Any fields deleted and re-inserted are always appended to the header
		list.
		"""
		return [v for k, v in self._headers]

	def items(self):
		"""Get all the header fields and values.

		These will be sorted in the order they were in the original header
		list, or were added to this instance, and may contain duplicates.
		Any fields deleted and re-inserted are always appended to the header
		list.
		"""
		return self._headers[:]

	def __repr__(self):
		return "Headers(%s)" % `self._headers`

	def __str__(self):
		"""str() returns the formatted headers, complete with end line,
		suitable for direct HTTP transmission."""
		return '\r\n'.join(["%s: %s" % kv for kv in self._headers]+['',''])

	def setdefault(self,name,value):
		"""Return first matching header value for 'name', or 'value'

		If there is no header named 'name', add a new header with name 'name'
		and value 'value'."""
		result = self.get(name)
		if result is None:
			self._headers.append((name,value))
			return value
		else:
			return result


	def add_header(self, _name, _value, **_params):
		"""Extended header setting.

		_name is the header field to add. keyword arguments can be used to set
		additional parameters for the header field, with underscores converted
		to dashes. Normally the parameter will be added as key="value" unless
		value is None, in which case only the key will be added.

		Example:

		h.add_header('content-disposition', 'attachment', filename='bud.gif')

		Note that unlike the corresponding 'email.Message' method, this does
		*not* handle '(charset, language, value)' tuples: all values must be
		strings or None.
		"""
		parts = []
		if _value is not None:
			parts.append(_value)
		for k, v in _params.items():
			if v is None:
				parts.append(k.replace('_', '-'))
			else:
				parts.append(_formatparam(k.replace('_', '-'), v))
		self._headers.append((_name, "; ".join(parts)))

	def elements(self, key):
		"""Return a list of HeaderElements for the given header (or None)."""
		key = str(key).title()
		h = self.get(key)
		if h is None:
			return []
		return header_elements(key, h)

###
### Defaults/Constants
###

SERVER_VERSION = "circuits/%s" % circuits.__version__
SERVER_PROTOCOL = "HTTP/1.1"
BUFFER_SIZE = 131072

DEFAULT_ERROR_MESSAGE = """\
<head>
<title>Error response</title>
</head>
<body>
<h1>Error response</h1>
<p>Error code %(code)d.
<p>Message: %(message)s.
<p>Error code explanation: %(code)s = %(explain)s.
<pre>%(traceback)s</pre>
</body>
"""

###
### Supporting Functions
###

quoted_slash = re.compile("(?i)%2F")

def quoteHTML(html):
	return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

image_map_pattern = re.compile(r"[0-9]+,[0-9]+")

def parseQueryString(query_string, keep_blank_values=True):
	"""parseQueryString(query_string) -> dict

	Build a params dictionary from a query_string.
	If keep_blank_values is True (the default), keep
	values that are blank.
	"""

	if image_map_pattern.match(query_string):
		# Server-side image map. Map the coords to "x" and "y"
		# (like CGI::Request does).
		pm = query_string.split(",")
		pm = {"x": int(pm[0]), "y": int(pm[1])}
	else:
		pm = cgi.parse_qs(query_string, keep_blank_values)
		for key, val in pm.items():
			if len(val) == 1:
				pm[key] = val[0]
	return pm


def parseHeaders(data):
	headers = Headers([])
		
	while True:
		line = data.readline()
		if not line:
			# No more data--illegal end of headers
			raise ValueError("Illegal end of headers.")
		
		if line == "\r\n":
			# Normal end of headers
			break
		
		if line[0] in " \t":
			# It's a continuation line.
			v = line.strip()
		else:
			k, v = line.split(":", 1)
			k, v = k.strip(), v.strip()

		headers.add_header(k, v)
		
	return headers, data.read()

def processBody(headers, body):
	if "Content-Type" not in headers:
		headers["Content-Type"] = ""
	
	try:
		form = FieldStorage(fp=body,
			headers=headers,
			environ={"REQUEST_METHOD": "POST"},
			keep_blank_values=True)
	except Exception, e:
		if e.__class__.__name__ == 'MaxSizeExceeded':
			# Post data is too big
			raise cherrypy.HTTPError(413)
		else:
			raise
	
	if form.file:
		return form.file
	else:
		return dictform(form)

def dictform(form):
	d = {}
	for key in form.keys():
		values = form[key]
		if isinstance(values, list):
			d[key] = []
			for item in values:
				if item.filename is not None:
					value = item # It's a file upload
				else:
					value = item.value # It's a regular field
				d[key].append(value)
		else:
			if values.filename is not None:
				value = values # It's a file upload
			else:
				value = values.value # It's a regular field
			d[key] = value
	return d

def compressBuf(buf):
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode="wb",  fileobj=zbuf, compresslevel=1)
	zfile.write(buf)
	zfile.close()
	zbuf.flush()
	zbuf.seek(0)
	return zbuf

###
### Events
###

class Request(Event):
	"""Request(Event) -> Request Event

	args: request, response
	"""

class Response(Event):
	"""Response(Event) -> Response Event

	args: request, response
	"""

class Stream(Event):
	"""Stream(Event) -> Stream Event

	args: request, response
	"""

class Write(Event):
	"""Write(Event) -> Write Event

	args: sock, data
	"""

class Close(Event):
	"""Close(Event) -> Close Event

	args: sock
	"""

###
### Supporting Classes
###

class _Request(object):
	"""_Request(method, path, version, qa, headers) -> new HTTP Request object

	Request object that holds an incoming request.
	"""

	app = None
	script_name = ""
	protocol = (1, 1)

	def __init__(self, method, path, version, qs, headers):
		"initializes x; see x.__class__.__doc__ for signature"

		self.method = method
		self.path = self.path_info = path
		self.version = version
		self.qs = self.query_string = qs
		self.headers = headers
		self.cookie = SimpleCookie()

		if "Cookie" in self.headers:
			self.cookie.load(self.headers["Cookie"])

		self.body = StringIO()

	def __repr__(self):
		return "<Request %s %s %s>" % (self.method, self.path, self.version)

class _Response(object):
	"""_Response(sock) -> new Response object

	A Response object that holds the response to
	send back to the client. This ensure that the correct data
	is sent in the correct order.
	"""

	def __init__(self, sock):
		"initializes x; see x.__class__.__doc__ for signature"

		self.sock = sock
		self.close = False
		
		self.headers = Headers([
			("Server", SERVER_VERSION),
			("Date", strftime("%a, %d %b %Y %H:%M:%S %Z"))])
		self.cookie = SimpleCookie()

		self.stream = False
		self.gzip = False
		self.body = ""
		self.time = time()
		self.status = "200 OK"

	def __repr__(self):
		return "<Response %s %s (%d)>" % (
				self.status,
				self.headers["Content-Type"],
				(len(self.body) if type(self.body) == str else 0))
	
	def __str__(self):
		status = self.status
		headers = self.headers
		body = self.process()
		return "%s %s\r\n%s%s" % (SERVER_PROTOCOL, status, headers, body or "")

	def process(self):
		for k, v in self.cookie.iteritems():
			self.headers.add_header("Set-Cookie", v.OutputString())

		if type(self.body) == file:
			cType = self.headers.get("Content-Type", "application/octet-stream")
			if self.gzip:
				self.body = compressBuf(self.body.read())
				self.headers["Content-Encoding"] = "gzip"
				self.body.seek(0, 2)
				cLen = self.body.tell()
				self.body.seek(0)
			else:
				cLen = os.fstat(self.body.fileno())[stat.ST_SIZE]

			if cLen > BUFFER_SIZE:
				body = self.body.read(BUFFER_SIZE)
				self.stream = True
			else:
				body = self.body.read()
		elif type(self.body) == str:
			body = self.body
			if self.gzip:
				body = compressBuf(body).getvalue()
				self.headers["Content-Encoding"] = "gzip"
			cLen = len(body)
			cType = self.headers.get("Content-Type", "text/html")
		else:
			body = ""
			cLen = 0
			cType = "text/plain"

		self.headers["Content-Type"] = cType
		self.headers["Content-Length"] = str(cLen)

		return body

###
### Dispatcher
###

class Dispatcher(Component):

	defaults = ["index.html"]
	docroot = os.getcwd()

	def findChannel(self, request):
		"""findChannel(request) -> channel

		Find and return an appropiate channel
		for the given request.

		The channel is found by traversing the system's event channels,
		and matching path components to successive channels in the system.

		If a channel cannot be found for a given path, but there is
		a default channel, then this will be used.

		The following is an example mappiny of path to channel given
		the following channels:

		Channels:
		 /:index
		 /foo:index
		 /foo:hello
		 /bar:GET
		 /bar:POST
		 /foo/bar/hello

		Method    Path                   Channel            VPath
		---------------------------------------------------------
		GET       /                      /                  []
		GET       /1/2/3                 /                  [1, 2, 3]
		GET       /foo                   /foo               []
		GET       /foo/hello             /foo/hello         []
		GET       /foo/1/2/3             /foo               [1, 2, 3]
		GET       /foo/hello/1/2/3       /foo/hello         [1, 2, 3]
		GET       /bar                   /bar               []
		GET       /bar/1/2/3             /bar               [1, 2, 3]
		POST      /bar                   /bar               []
		POST      /bar/1/2/3             /bar               [1, 2, 3]
		GET       /foo/bar/hello         /foo/bar/hello     []
		GET       /foo/bar/hello/1/2/3   /foo/bar/hello     [1, 2, 3]
		"""

		path = request.path
		method = request.method.upper()
		names = [x for x in path.strip('/').split('/') if x]
		defaults = ["index", method]

		if not names:
			for default in defaults:
				k = "/:%s" % default
				if k in self.manager.channels:
					return k, []
			return None, []

		targets = set([x.split(":")[0] for x in self.manager.channels if x and \
				":" in x and x[0] == "/"])

		i = 0
		matches = [""]
		candidates = []
		while i <= len(names):
			x = "/".join(matches) or "/"
			if x in targets:
				candidates.append([i, x])
				if i < len(names):
					matches.append(names[i])
			else:
				break
			i += 1

		if not candidates:
			return None, []

		i, candidate = candidates.pop()

		if i < len(names):
			channels = [names[i], "index", method]
		else:
			channels = ["index", method]

		vpath = []
		channel = None
		for ch in channels:
			x = "%s:%s" % (candidate, ch)
			found = x in self.manager.channels
			if found:
				if i < len(names) and ch == names[i]:
					i += 1
				channel = x
				break

		if channel is not None:
			if i < len(names):
				vpath = names[i:]
				vpath = [x.replace("%2F", "/") for x in vpath]
			else:
				vpath = []

		return channel, vpath

	@listener("request")
	def onREQUEST(self, request, response):
		path = request.path.strip("/")
		if path:
			filename = os.path.abspath(os.path.join(self.docroot, path))
		else:
			for default in self.defaults:
				filename = os.path.abspath(os.path.join(self.docroot, default))
				if os.path.exists(filename):
					break
				else:
					filename = None

		if filename and os.path.exists(filename):
			expires(3500*24*30)
			serve_file(filename)
			return self.send(Response(response), "response")

		channel, vpath = self.findChannel(request)
	
		if channel:
			params = parseQueryString(request.qs)
			x = processBody(request.headers, request.body)
			if type(x) == dict:
				params.update(x)
			else:
				request.body = x
			
			req = Request(request, response, *vpath, **params)
			try:
				res = [x for x in self.iter(req, channel) if type(x) == str]
			except Exception, error:
				raise
			if res:
				response.body = res[0]
				return self.send(Response(response), "response")
			else:
				raise NotFound()
		else:
			raise NotFound()

###
### Protocol Component
###

class HTTP(Component):
	"""HTTP() -> HTTP Component

	Create a new HTTP object which implements the HTTP
	protocol. Note this doesn"t actually do anything
	usefull unless used in conjunction with either:
	 * circuits.parts.sockets.TCPClient or
	 * circuits.parts.sockets.TCPServer

	Sub-classes that wish to do something usefull with
	events that are processed and generated, must have
	filters/listeners associated with them. For instance,
	to do something with ... events:

	{{{
	#!python
	class Client(HTTP):

		@listener("...")
		def on...(self, ...):
			...
	}}}

	The available events that are processed and generated
	are pushed onto channels associated with that event.
	They are:
	 * ...
	"""

	_requests = {}

	###
	### Event Processing
	###

	@listener("stream")
	def onSTREAM(self, response):
		data = response.body.read(BUFFER_SIZE)
		if data:
			self.send(Write(response.sock, data), "write")
			self.push(Stream(response), "stream")
		else:
			response.body.close()
			if response.close:
				self.send(Close(response.sock), "close")
		
	@listener("response")
	def onRESPONSE(self, response):
		self.send(Write(response.sock, str(response)), "write")
		if response.stream:
			self.push(Stream(response), "stream")
		elif response.close:
			self.send(Close(response.sock), "close")

	@listener("read")
	def onREAD(self, sock, data):
		"""H.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard HTTP delimiter
		\r\n and create a RawEvent per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		if sock in self._requests:
			request = self._requests[sock]
			request.body.write(data)
			contentLength = int(request.headers.get("Content-Length", "0"))
			if not request.body.tell() == contentLength:
				return
		else:
			requestline, data = re.split("\r?\n", data, 1)
			method, path, protocol = requestline.strip().split(" ", 2)
			scheme, location, path, params, qs, frag = urlparse(path)

			if frag:
				return self.sendError(sock, 400,
						"Illegal #fragment in Request-URI.")
		
			if params:
				path = path + ";" + params
		
			# Unquote the path+params (e.g. "/this%20path" -> "this path").
			# http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
			#
			# But note that "...a URI must be separated into its components
			# before the escaped characters within those components can be
			# safely decoded." http://www.ietf.org/rfc/rfc2396.txt, sec 2.4.2
			atoms = [unquote(x) for x in quoted_slash.split(path)]
			path = "%2F".join(atoms)
		
			# Compare request and server HTTP protocol versions, in case our
			# server does not support the requested protocol. Limit our output
			# to min(req, server). We want the following output:
			#	 request	server	 actual written supported response
			#	 protocol protocol response protocol	feature set
			# a	 1.0		1.0			1.0				1.0
			# b	 1.0		1.1			1.1				1.0
			# c	 1.1		1.0			1.0				1.0
			# d	 1.1		1.1			1.1				1.1
			# Notice that, in (b), the response will be "HTTP/1.1" even though
			# the client only understands 1.0. RFC 2616 10.5.6 says we should
			# only return 505 if the _major_ version is different.
			rp = int(protocol[5]), int(protocol[7])
			sp = int(SERVER_PROTOCOL[5]), int(SERVER_PROTOCOL[7])
			if sp[0] != rp[0]:
				return self.sendError(sock, 505, "HTTP Version Not Supported")

			assert "\r\n\r\n" in data
			headers, body = parseHeaders(StringIO(data))

			request = _Request(method, path, protocol, qs, headers)
			request.body.write(body)

			if headers.get("Expect", "") == "100-continue":
				self._requests[sock] = request
				self.sendSimple(sock, 100)
				return

			contentLength = int(headers.get("Content-Length", "0"))
			if not request.body.tell() == contentLength:
				self._requests[sock] = request
				return

		response = _Response(sock)

		response.gzip = "gzip" in request.headers.get("Accept-Encoding", "")

		if cherrypy:
			cherrypy.request = request
			cherrypy.response = response

		# Persistent connection support
		if request.protocol == "HTTP/1.1":
			# Both server and client are HTTP/1.1
			if request.headers.get("HTTP_CONNECTION", "") == "close":
				response.close = True
		else:
			# Either the server or client (or both) are HTTP/1.0
			if request.headers.get("HTTP_CONNECTION", "") != "Keep-Alive":
				response.close = True

		request.body.seek(0)

		try:
			self.send(Request(request, response), "request")
		except HTTPRedirect, error:
			error.set_response()
			self.send(Response(response), "response")
		except HTTPError, error:
			self.sendError(sock, error[0], error[1], response)
		except Exception, error:
			self.sendError(sock, 500, "Internal Server Error", format_exc(), response)
		finally:
			if sock in self._requests:
				del self._requests[sock]

	###
	### Supporting Functions
	###

	def sendSimple(self, sock, code, message=""):
		"""H.sendSimple(sock, code, message="")

		Send a simple response.
		"""

		try:
			short, long = RESPONSES[code]
		except KeyError:
			short, long = "???", "???"

		if not message:
			message = short

		response = _Response(sock)
		response.body = message
		response.status = "%s %s" % (code, message)

		if response.status[:3] == "413" and response.protocol == "HTTP/1.1":
			# Request Entity Too Large
			response.close = True
			response.headers.add_header("Connection", "close")

		self.send(Response(response), "response")

		if response.close:
			self.send(Close(sock), "close")

	def sendError(self, sock, code, message=None, traceback=None, response=None):
		"""H.sendError(sock, code, message=None, traceback=None, response=None) -> None
		
		Send an error reply.

		Arguments are the error code, and a detailed message.
		The detailed message defaults to the short entry matching the
		response code.

		This sends an error response (so it must be called before any
		output has been generated), and sends a piece of HTML explaining
		the error to the user.
		"""

		try:
			short, long = RESPONSES[code]
		except KeyError:
			short, long = "???", "???"

		if message is None:
			message = short

		explain = long

		content = DEFAULT_ERROR_MESSAGE % {
			"code": code,
			"message": quoteHTML(message),
			"explain": explain,
			"traceback": traceback or ""}

		if response is None:
			response = _Response(sock)
		response.body = content
		response.status = "%s %s" % (code, message)
		response.headers.add_header("Connection", "close")

		self.send(Response(response), "response")

		self.send(Close(sock), "close")

###
### Response Codes
###

RESPONSES = {
	100: ("Continue", "Request received, please continue"),
	101: ("Switching Protocols",
		"Switching to new protocol; obey Upgrade header"),

	200: ("OK", "Request fulfilled, document follows"),
	201: ("Created", "Document created, URL follows"),
	202: ("Accepted",
		"Request accepted, processing continues off-line"),
	203: ("Non-Authoritative Information", "Request fulfilled from cache"),
	204: ("No Content", "Request fulfilled, nothing follows"),
	205: ("Reset Content", "Clear input form for further input."),
	206: ("Partial Content", "Partial content follows."),

	300: ("Multiple Choices",
		"Object has several resources -- see URI list"),
	301: ("Moved Permanently", "Object moved permanently -- see URI list"),
	302: ("Found", "Object moved temporarily -- see URI list"),
	303: ("See Other", "Object moved -- see Method and URL list"),
	304: ("Not Modified",
		"Document has not changed since given time"),
	305: ("Use Proxy",
		"You must use proxy specified in Location to access this "
		"resource."),
	307: ("Temporary Redirect",
		"Object moved temporarily -- see URI list"),

	400: ("Bad Request",
		"Bad request syntax or unsupported method"),
	401: ("Unauthorized",
		"No permission -- see authorization schemes"),
	402: ("Payment Required",
		"No payment -- see charging schemes"),
	403: ("Forbidden",
		"Request forbidden -- authorization will not help"),
	404: ("Not Found", "Nothing matches the given URI"),
	405: ("Method Not Allowed",
		"Specified method is invalid for this server."),
	406: ("Not Acceptable", "URI not available in preferred format."),
	407: ("Proxy Authentication Required", "You must authenticate with "
		"this proxy before proceeding."),
	408: ("Request Timeout", "Request timed out; try again later."),
	409: ("Conflict", "Request conflict."),
	410: ("Gone",
		"URI no longer exists and has been permanently removed."),
	411: ("Length Required", "Client must specify Content-Length."),
	412: ("Precondition Failed", "Precondition in headers is false."),
	413: ("Request Entity Too Large", "Entity is too large."),
	414: ("Request-URI Too Long", "URI is too long."),
	415: ("Unsupported Media Type", "Entity body in unsupported format."),
	416: ("Requested Range Not Satisfiable",
		"Cannot satisfy request range."),
	417: ("Expectation Failed",
		"Expect condition could not be satisfied."),

	500: ("Internal Server Error", "Server got itself in trouble"),
	501: ("Not Implemented",
		"Server does not support this operation"),
	502: ("Bad Gateway", "Invalid responses from another server/proxy."),
	503: ("Service Unavailable",
		"The server cannot process the request due to a high load"),
	504: ("Gateway Timeout",
		"The gateway server did not receive a timely response"),
	505: ("HTTP Version Not Supported", "Cannot fulfill request."),
}
