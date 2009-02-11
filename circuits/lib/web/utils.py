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

def url(request, path="", qs="", script_name=None, base=None, relative=None):
    """Create an absolute URL for the given path.
    
    If 'path' starts with a slash ('/'), this will return
        (base + script_name + path + qs).
    If it does not start with a slash, this returns
        (base + script_name [+ request.path_info] + path + qs).
    
    If script_name is None, request will be used
    to find a script_name, if available.
    
    If base is None, request.base will be used (if available).
    
    Finally, note that this function can be used to obtain an absolute URL
    for the current request path (minus the querystring) by passing no args.
    If you call url(qs=request.query_string), you should get the
    original browser URL (assuming no internal redirections).
    
    If relative is None or not provided, request.app.relative_urls will
    be used (if available, else False). If False, the output will be an
    absolute URL (including the scheme, host, vhost, and script_name).
    If True, the output will instead be a URL that is relative to the
    current request path, perhaps including '..' atoms. If relative is
    the string 'server', the output will instead be a URL that is
    relative to the server root; i.e., it will start with a slash.
    """
    if qs:
        qs = '?' + qs
    
    if request.app:
        if not path.startswith("/"):
            # Append/remove trailing slash from path_info as needed
            # (this is to support mistyped URL's without redirecting;
            # if you want to redirect, use tools.trailing_slash).
            pi = request.path_info
            if request.is_index is True:
                if not pi.endswith('/'):
                    pi = pi + '/'
            elif request.is_index is False:
                if pi.endswith('/') and pi != '/':
                    pi = pi[:-1]
            
            if path == "":
                path = pi
            else:
                path = _urljoin(pi, path)
        
        if script_name is None:
            script_name = request.script_name
        if base is None:
            base = request.base
        
        newurl = base + script_name + path + qs
    else:
        # No request.app (we're being called outside a request).
        # We'll have to guess the base from server.* attributes.
        # This will produce very different results from the above
        # if you're using vhosts or tools.proxy.
        if base is None:
            base = request.server.base()
        
        path = (script_name or "") + path
        newurl = base + path + qs
    
    if './' in newurl:
        # Normalize the URL by removing ./ and ../
        atoms = []
        for atom in newurl.split('/'):
            if atom == '.':
                pass
            elif atom == '..':
                atoms.pop()
            else:
                atoms.append(atom)
        newurl = '/'.join(atoms)
    
    # At this point, we should have a fully-qualified absolute URL.
    
    if relative is None:
        relative = getattr(request.app, "relative_urls", False)
    
    # See http://www.ietf.org/rfc/rfc2396.txt
    if relative == 'server':
        # "A relative reference beginning with a single slash character is
        # termed an absolute-path reference, as defined by <abs_path>..."
        # This is also sometimes called "server-relative".
        newurl = '/' + '/'.join(newurl.split('/', 3)[3:])
    elif relative:
        # "A relative reference that does not begin with a scheme name
        # or a slash character is termed a relative-path reference."
        old = url().split('/')[:-1]
        new = newurl.split('/')
        while old and new:
            a, b = old[0], new[0]
            if a != b:
                break
            old.pop(0)
            new.pop(0)
        new = (['..'] * len(old)) + new
        newurl = '/'.join(new)
    
    return newurl
