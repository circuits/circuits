# Module:	smtp
# Date:		13th June 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Simple Mail Transfer Protocol

This module implements the Simple Mail Transfer Protocol
or commonly known as SMTP.
"""

import re
import socket
from tempfile import TemporaryFile

from circuits import handler, Event, Component

###
### Supporting Functions
###

LINESEP = re.compile("\r?\n")

def splitLines(s, buffer):
	"""splitLines(s, buffer) -> lines, buffer

	Append s to buffer and find any new lines of text in the
	string splitting at the standard IRC delimiter CRLF. Any
	new lines found, return them as a list and the remaining
	buffer for further processing.
	"""

	lines = LINESEP.split(buffer + s)
	return lines[:-1], lines[-1]

def stripAddress(address):
	"""stripAddress(address) -> address

	Strip the leading & trailing <> from an address.
	Handy for getting FROM: addresses.
	"""

	start = address.index("<") + 1
	end = address.index(">")

	return address[start:end]

def splitTo(address):
	"""splitTo(address) -> (host, fulladdress)

	Return 'address' as undressed (host, fulladdress) tuple.
	Handy for use with TO: addresses.
	"""

	start = address.index("<") + 1
	sep = address.index("@") + 1
	end = address.index(">")

	return (address[sep:end], address[start:end],)

def getAddress(keyword, arg):
	address = None
	keylen = len(keyword)
	if arg[:keylen].upper() == keyword:
		address = arg[keylen:].strip()
		if not address:
			pass
		elif address[0] == "<" and address[-1] == ">" and address != "<>":
			# Addresses can be in the form <person@dom.com> but watch out
			# for null address, e.g. <>
			address = address[1:-1]
	return address

###
### Events
###

class Raw(Event): pass
class Helo(Event): pass
class Mail(Event): pass
class Rcpt(Event): pass
class Data(Event): pass
class Rset(Event): pass
class Noop(Event): pass
class Quit(Event): pass
class Message(Event): pass

###
### Protocol Class
###

class SMTP(Component):
	"""SMTP(event) -> new smtp object

	Create a new smtp object which implements the SMTP
	protocol. Note this doesn't actually do anything
	usefull unless used in conjunction with
	circuits.parts.sockets.TCPServer.

	See: examples/net/smtpd.py
	"""

	COMMAND = 0
	DATA = 1

	__buffers = {}

	__states = {}

	__greeting = None
	__mailfrom = None
	__rcpttos = []
	__data = None

	__fqdn = socket.getfqdn()

	###
	### Methods
	###

	def reset(self):
		self.__buffers = {}
		self.__states = {}
		self.__greeting = None
		self.__mailfrom = None
		self.__rcpttos = []
		self.__data = None

	def processMessage(self, sock, mailfrom, rcpttos, data):
		r =  self.send(Message(sock, mailfrom, rcpttos, data), "message")
		data.close()

		if r:
			return r[-1]

	###
	### Properties
	###

	def getFQDN(self):
		"""I.getFQDN() -> str

		Return the fully qualified domain name of this server.
		"""

		return self.__fqdn

	###
	### Event Processing
	###

	@handler("raw")
	def onRAW(self, sock, line):
		"""I.onRAW(sock, line) -> None

		Process a line of text and generate the appropiate
		event. This must not be overridden by sub-classes,
		if it is, this must be explitetly called by the
		sub-class. Other Components may however listen to
		this event and process custom SMTP events.
		"""

		if self.__states[sock] == self.COMMAND:
			if not line:
				self.write(sock, "500 Syntax error, command unrecognized\r\n")
				return

			method = None

			i = line.find(" ")
			if i < 0:
				command = line.upper()
				arg = None
			else:
				command = line[:i].upper()
				arg = line[i+1:].strip()

			method = getattr(self, "smtp" + command, None)

			if not method:
				self.write(sock, "502 Command not implemented\r\n")
			else:
				method(sock, arg)
		else:
			if self.__states[sock] != self.DATA:
				self.write(sock, "451 Internal confusion\r\n")
				return

			if line and re.match("^\.$", line):
					self.__data.flush()
					self.__data.seek(0)
					status = self.processMessage(sock,
							self.__mailfrom,  self.__rcpttos, self.__data)

					self.reset()

					if not status:
						self.write(sock, "250 Ok\r\n")
					else:
						self.write(sock, status + "\r\n")
			else:
				if line and line[0] == ".":
					self.__data.write(line[1:] + "\n")
				else:
					self.__data.write(line + "\n")

	###
	### SMTP and ESMTP Commands
	###

	def smtpHELO(self, sock, arg):
		if not arg:
			self.write(sock, "501 Syntax: HELO hostname\r\n")
			return

		if self.__greeting:
			self.write(sock, "503 Duplicate HELO/EHLO\r\n")
		else:
			self.__greeting = arg
			self.write(sock, "250 %s\r\n" % self.__fqdn)
			self.push(Helo(sock, arg), "helo", self.channel)

	def smtpNOOP(self, sock, arg):
		if arg:
			self.write(sock, "501 Syntax: NOOP\r\n")
		else:
			self.write(sock, "250 Ok\r\n")
			self.push(Noop(sock), "noop", self.channel)

	def smtpQUIT(self, sock, arg):
		self.write(sock, "221 Bye\r\n")
		self.close(sock)
		self.push(Quit(sock), "quit", self.channel)

	def smtpMAIL(self, sock, arg):
		address = getAddress("FROM:", arg)

		if not address:
			self.write(sock, "501 Syntax: MAIL FROM:<address>\r\n")
			return

		if self.__mailfrom:
			self.write(sock, "503 Error: nested MAIL command\r\n")
			return

		self.__mailfrom = address

		self.write(sock, "250 Ok\r\n")
		self.push(Mail(sock, address), "mail", self.channel)

	def smtpRCPT(self, sock, arg):
		if not self.__mailfrom:
			self.write(sock, "503 Error: need MAIL command\r\n")
			return

		address = getAddress("TO:", arg)

		if not address:
			self.write(sock, "501 Syntax: RCPT TO: <address>\r\n")
			return

		self.__rcpttos.append(address)
		self.write(sock, "250 Ok\r\n")
		self.push(Rcpt(sock, address), "rcpt", self.channel)

	def smtpRSET(self, sock, arg):
		if arg:
			self.write(sock, "501 Syntax: RSET\r\n")
			return

		# Resets the sender, recipients, and data, but not the greeting
		self.__mailfrom[sock] = None
		self.__rcpttos = []
		self.__data = None
		self.__states = {}
		self.write(sock, "250 Ok\r\n")
		self.push(Rset(sock), "rset", self.channel)

	def smtpDATA(self, sock, arg):
		if not self.__rcpttos:
			self.write(sock, "503 Error: need RCPT command\r\n")
			return

		if arg:
			self.write(sock, "501 Syntax: DATA\r\n")
			return

		self.__state = self.DATA
		self.__data = TemporaryFile()

		self.write(sock, "354 End data with <CR><LF>.<CR><LF>\r\n")
		self.push(Data(sock), "data", self.channel)

	###
	### Default Socket Events
	###

	@handler("connect")
	def onCONNECT(self, sock, host, port):
		self.__states[sock] = self.COMMAND
		self.__buffers[sock] = ""
		self.write(sock, "220 %s ???\r\n" % self.__fqdn)

	@handler("disconnect")
	def onDISCONNECT(self, sock):
		self.reset()

	@handler("read")
	def onREAD(self, sock, data):
		"""S.onREAD(sock, data) -> None

		Process any incoming data appending it to an internal
		buffer. Split the buffer by the standard line delimiters
		CRLF and create a Raw event per line. Any unfinished
		lines of text, leave in the buffer.
		"""

		lines, buffer = splitLines(data, self.__buffers[sock])
		self.__buffers[sock] = buffer
		for line in lines:
			self.push(Raw(sock, line), "raw", self.channel)
