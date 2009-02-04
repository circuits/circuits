# Module:	utils
# Date:		13th September 2007
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Utilities

This module implements utility functions.
"""

import re
import cgi
from gzip import GzipFile
from cStringIO import StringIO

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
	zbuf = StringIO()
	zfile = GzipFile(mode="wb",  fileobj=zbuf, compresslevel=1)
	zfile.write(buf)
	zfile.close()
	zbuf.flush()
	zbuf.seek(0)
	return zbuf
