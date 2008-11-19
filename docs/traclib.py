# Module:	traclib
# Date:		19th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Trac Library

Trac XML-RPC Library
"""

import os
import re
import readline
import optparse
import tempfile
import xmlrpclib
from cStringIO import StringIO
from traceback import format_exc

__version__ = "0.1"
__author__ = "James Mills"

USAGE = "%prog <options> [<page>]"
VERSION = "%prog v" + __version__

###
### Errors
###

class Error(Exception): pass

class NotFound(Error):

	def __init__(self, page):
		super(NotFound, self).__init__()

		self.page = page

	def __repr__(self):
		return "NotFound: %s not found" % self.page

class NotModified(Error):

	def __init__(self, page):
		super(NotModified, self).__init__()

		self.page = page

	def __repr__(self):
		return "NotModified: %s not modified" % self.page

###
### Functions
###

def parse_options():
	"""parse_options() -> opts, args

	Parse any command-line options given returning both
	the parsed options and arguments.
	"""

	parser = optparse.OptionParser(usage=USAGE, version=VERSION)

	parser.add_option("-l", "--list",
			action="store_true", default=False, dest="list",
			help="List wiki all pages")
	parser.add_option("-e", "--edit",
			action="store_true", default=False, dest="edit",
			help="Edit a wiki page")
	parser.add_option("-s", "--save",
			action="store_true", default=False, dest="save",
			help="Save a wiki page locally")
	parser.add_option("-d", "--delete",
			action="store_true", default=False, dest="delete",
			help="Delete a wiki page")
	parser.add_option("-u", "--upload",
			action="store_true", default=False, dest="upload",
			help="Upload a wiki page")
	parser.add_option("-c", "--comment",
			action="store", default=None, dest="comment",
			help="Specify a comment")

	opts, args = parser.parse_args()

	return opts, args

###
### Components
###

class Trac(object):

	uri = None

	def __init__(self, opts, uri=None):
		self.opts = opts
		self.uri = os.getenv("TRACURL", uri)

		self.server = xmlrpclib.ServerProxy(self.uri)

	def pages(self):
		pages = self.server.wiki.getAllPages()
		pages.sort()
		return pages

	def _getPage(self, page):
		info = self.server.wiki.getPageInfo(page)

		if not type(info) == dict:
			raise NotFound(page)

		try:
			content = self.server.wiki.getPage(page)
			content = content.encode("utf-8")
		except xmlrpclib.Fault, fault:
			raise

		return content

	def _savePage(self, page, content, **kwargs):
		try:
			self.server.wiki.putPage(page, content, kwargs)
		except xmlrpclib.Fault, fault:
			if re.match("^'Page not modified'.*", fault.faultString):
				raise NotModified(page)
			else:
				raise

	def _deletePage(self, page):
		try:
			self.server.wiki.deletePage(page)
		except xmlrpclib.Fault, fault:
			raise

	def edit(self, page, comment=None):
		editor = os.getenv("EDITOR", "vim")
		user = os.getenv("USER", "anonymous")

		try:
			content = self._getPage(page)
		except NotFound:
			content = ""

		buffer = tempfile.NamedTemporaryFile(prefix="trac", suffix=".wiki")
		buffer.write(content)
		buffer.flush()
		buffer.seek(0)

		os.system("%s %s" % (editor, buffer.name))
		buffer.flush()
		buffer.seek(0)
		content = buffer.read()
		buffer.close()

		comment = comment or self.opts.comment or raw_input("Comment: ")

		self._savePage(page, content, author=user, comment=comment)

	def save(self, page):
		content = self._getPage(page)
		filename = page.replace("/", "_")
		buffer = open("%s.wiki" % filename, "w")
		buffer.write(content)
		buffer.flush()
		buffer.close()

	def delete(self, page):
		q = raw_input("Delete %s (y/n) ?" % page)
		if q == "y":
			self._deletePage(page)

	def upload(self, page, filename, comment=None):
		user = os.getenv("USER", "anonymous")

		fd = open(filename, "r")
		content = fd.read()
		fd.close()

		comment = comment or self.opts.comment or raw_input("Comment: ")

		self._savePage(page, content, author=user, comment=comment)

###
### Main
###

def main():
	opts, args = parse_options()

	if args:
		page = args[0]
	else:
		page = None

	trac = Trac(opts)

	if opts.list:
		for page in trac.pages():
			print page
	elif opts.edit:
		try:
			trac.edit(page)
		except KeyboardInterrupt:
			pass
		except Exception, error:
			print "ERROR: %s" % error
			print format_exc()
	elif opts.save:
		try:
			trac.save(page)
		except Exception, error:
			print "ERROR: %s" % error
			print format_exc()
	elif opts.delete:
		try:
			trac.delete(page)
		except Exception, error:
			print "ERROR: %s" % error
			print format_exc()
	elif opts.upload:
		try:
			trac.upload(*args)
		except Exception, error:
			print "ERROR: %s" % error
			print format_exc()

###
### Entry Point
###

if __name__ == "__main__":
	main()
