# Module:   utils
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utilities

This module implements utility functions.
"""

import re
from gzip import GzipFile
from cStringIO import StringIO
from urlparse import urljoin as _urljoin

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from constants import RESPONSES

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
        return {"x": int(pm[0]), "y": int(pm[1])}
    else:
        pm = parse_qs(query_string, keep_blank_values)
        return dict((k, v[0]) for k, v in pm.iteritems() if v)

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
       - (base + script_name + path + qs).
    If it does not start with a slash, this returns
       - (base + script_name [+ request.path] + path + qs).
    
    If script_name is None, request will be used
    to find a script_name, if available.
    
    If base is None, request.base will be used (if available).
    
    Finally, note that this function can be used to obtain an absolute URL
    for the current request path (minus the querystring) by passing no args.
    If you call url(qs=request.qs), you should get the
    original browser URL (assuming no internal redirections).
    
    If relative is False the output will be an absolute URL
    (including the scheme, host, vhost, and script_name).
    If True, the output will instead be a URL that is relative to the
    current request path, perhaps including '..' atoms. If relative is
    the string 'server', the output will instead be a URL that is
    relative to the server root; i.e., it will start with a slash.
    """
    if qs:
        qs = '?' + qs
    
    if not path.startswith("/"):
        # Append/remove trailing slash from request.path as needed
        # (this is to support mistyped URL's without redirecting;
        # if you want to redirect, use tools.trailing_slash).
        pi = request.path
        if request.index is True:
            if not pi.endswith('/'):
                pi = pi + '/'
        elif request.index is False:
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

def valid_status(status):
    """Return legal HTTP status Code, Reason-phrase and Message.
    
    The status arg must be an int, or a str that begins with an int.
    
    If status is an int, or a str and  no reason-phrase is supplied,
    a default reason-phrase will be provided.
    """
    
    if not status:
        status = 200
    
    status = str(status)
    parts = status.split(" ", 1)
    if len(parts) == 1:
        # No reason supplied.
        code, = parts
        reason = None
    else:
        code, reason = parts
        reason = reason.strip()
    
    try:
        code = int(code)
    except ValueError:
        raise ValueError("Illegal response status from server "
                         "(%s is non-numeric)." % repr(code))
    
    if code < 100 or code > 599:
        raise ValueError("Illegal response status from server "
                         "(%s is out of range)." % repr(code))
    
    if code not in RESPONSES:
        # code is unknown but not illegal
        default_reason, message = "", ""
    else:
        default_reason, message = RESPONSES[code]
    
    if reason is None:
        reason = default_reason
    
    return code, reason, message

def get_ranges(headervalue, content_length):
    """Return a list of (start, stop) indices from a Range header, or None.
    
    Each (start, stop) tuple will be composed of two ints, which are suitable
    for use in a slicing operation. That is, the header "Range: bytes=3-6",
    if applied against a Python string, is requesting resource[3:7]. This
    function will return the list [(3, 7)].
    
    If this function returns an empty list, you should return HTTP 416.
    """
    
    if not headervalue:
        return None
    
    result = []
    bytesunit, byteranges = headervalue.split("=", 1)
    for brange in byteranges.split(","):
        start, stop = [x.strip() for x in brange.split("-", 1)]
        if start:
            if not stop:
                stop = content_length - 1
            start, stop = map(int, (start, stop))
            if start >= content_length:
                # From rfc 2616 sec 14.16:
                # "If the server receives a request (other than one
                # including an If-Range request-header field) with an
                # unsatisfiable Range request-header field (that is,
                # all of whose byte-range-spec values have a first-byte-pos
                # value greater than the current length of the selected
                # resource), it SHOULD return a response code of 416
                # (Requested range not satisfiable)."
                continue
            if stop < start:
                # From rfc 2616 sec 14.16:
                # "If the server ignores a byte-range-spec because it
                # is syntactically invalid, the server SHOULD treat
                # the request as if the invalid Range header field
                # did not exist. (Normally, this means return a 200
                # response containing the full entity)."
                return None
            result.append((start, stop + 1))
        else:
            if not stop:
                # See rfc quote above.
                return None
            # Negative subscript (last N bytes)
            result.append((content_length - int(stop), content_length))
    
    return result
