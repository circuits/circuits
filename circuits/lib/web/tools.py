# Module:   tools
# Date:     16th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Tools

This module implements tools used throughout circuits.web.
These tools can also be used within Controlelrs and request handlers.
"""

import os
import stat
import types
import hashlib
import datetime
import mimetypes
import mimetools
from rfc822 import formatdate

mimetypes.init()
mimetypes.types_map['.dwg']='image/x-dwg'
mimetypes.types_map['.ico']='image/x-icon'

import _httpauth
from utils import url, valid_status, get_ranges
from errors import HTTPError, NotFound, Redirect, Unauthorized

def expires(request, response, secs=0, force=False):
    """Tool for influencing cache mechanisms using the 'Expires' header.
    
    'secs' must be either an int or a datetime.timedelta, and indicates the
    number of seconds between response.time and when the response should
    expire. The 'Expires' header will be set to (response.time + secs).
    
    If 'secs' is zero, the 'Expires' header is set one year in the past, and
    the following "cache prevention" headers are also set:
       - 'Pragma': 'no-cache'
       - 'Cache-Control': 'no-cache, must-revalidate'
    
    If 'force' is False (the default), the following headers are checked:
    'Etag', 'Last-Modified', 'Age', 'Expires'. If any are already present,
    none of the above response headers are set.
    """
    
    headers = response.headers
    
    cacheable = False
    if not force:
        # some header names that indicate that the response can be cached
        for indicator in ('Etag', 'Last-Modified', 'Age', 'Expires'):
            if indicator in headers:
                cacheable = True
                break
    
    if not cacheable:
        if isinstance(secs, datetime.timedelta):
            secs = (86400 * secs.days) + secs.seconds
        
        if secs == 0:
            if force or "Pragma" not in headers:
                headers["Pragma"] = "no-cache"
            if request.protocol >= (1, 1):
                if force or "Cache-Control" not in headers:
                    headers["Cache-Control"] = "no-cache, must-revalidate"
            # Set an explicit Expires date in the past.
            expiry = formatdate(1169942400.0)
        else:
            expiry = formatdate(response.time + secs)
        if force or "Expires" not in headers:
            headers["Expires"] = expiry


def serve_file(request, response, path, type=None, disposition=None, name=None):
    """Set status, headers, and body in order to serve the given file.
    
    The Content-Type header will be set to the type arg, if provided.
    If not provided, the Content-Type will be guessed by the file extension
    of the 'path' argument.
    
    If disposition is not None, the Content-Disposition header will be set
    to "<disposition>; filename=<name>". If name is None, it will be set
    to the basename of path. If disposition is None, no Content-Disposition
    header will be written.
    """
    
    if not os.path.isabs(path):
        raise ValueError("'%s' is not an absolute path." % path)
    
    try:
        st = os.stat(path)
    except OSError:
        return NotFound(request, response)
    
    # Check if path is a directory.
    if stat.S_ISDIR(st.st_mode):
        # Let the caller deal with it as they like.
        return NotFound(request, response)
    
    # Set the Last-Modified response header, so that
    # modified-since validation code can work.
    response.headers['Last-Modified'] = formatdate(st.st_mtime)
    validate_since(request, response)
    
    if type is None:
        # Set content-type based on filename extension
        ext = ""
        i = path.rfind('.')
        if i != -1:
            ext = path[i:].lower()
        type = mimetypes.types_map.get(ext, "text/plain")
    response.headers['Content-Type'] = type
    
    if disposition is not None:
        if name is None:
            name = os.path.basename(path)
        cd = '%s; filename="%s"' % (disposition, name)
        response.headers["Content-Disposition"] = cd
    
    # Set Content-Length and use an iterable (file object)
    #   this way CP won't load the whole file in memory
    c_len = st.st_size
    bodyfile = open(path, 'rb')
    
    # HTTP/1.0 didn't have Range/Accept-Ranges headers, or the 206 code
    if request.protocol >= (1, 1):
        response.headers["Accept-Ranges"] = "bytes"
        r = get_ranges(request.headers.get('Range'), c_len)
        if r == []:
            response.headers['Content-Range'] = "bytes */%s" % c_len
            message = "Invalid Range (first-byte-pos greater than Content-Length)"
            return HTTPError(request, response, 416, message)
        if r:
            if len(r) == 1:
                # Return a single-part response.
                start, stop = r[0]
                r_len = stop - start
                response.status = "206 Partial Content"
                response.headers['Content-Range'] = ("bytes %s-%s/%s" %
                                                       (start, stop - 1, c_len))
                response.headers['Content-Length'] = r_len
                bodyfile.seek(start)
                response.body = bodyfile.read(r_len)
            else:
                # Return a multipart/byteranges response.
                response.status = "206 Partial Content"
                boundary = mimetools.choose_boundary()
                ct = "multipart/byteranges; boundary=%s" % boundary
                response.headers['Content-Type'] = ct
                if response.headers.has_key("Content-Length"):
                    # Delete Content-Length header so finalize() recalcs it.
                    del response.headers["Content-Length"]
                
                def file_ranges():
                    # Apache compatibility:
                    yield "\r\n"
                    
                    for start, stop in r:
                        yield "--" + boundary
                        yield "\r\nContent-type: %s" % type
                        yield ("\r\nContent-range: bytes %s-%s/%s\r\n\r\n"
                               % (start, stop - 1, c_len))
                        bodyfile.seek(start)
                        yield bodyfile.read(stop - start)
                        yield "\r\n"
                    # Final boundary
                    yield "--" + boundary + "--"
                    
                    # Apache compatibility:
                    yield "\r\n"
                response.body = file_ranges()
        else:
            response.headers['Content-Length'] = c_len
            response.body = bodyfile
    else:
        response.headers['Content-Length'] = c_len
        response.body = bodyfile

    return response

def serve_download(request, response, path, name=None):
    """Serve 'path' as an application/x-download attachment."""

    type = "application/x-download"
    disposition = "attachment"

    return serve_file(request, response, path, type, disposition, name)

def validate_etags(request, response, autotags=False):
    """Validate the current ETag against If-Match, If-None-Match headers.
    
    If autotags is True, an ETag response-header value will be provided
    from an MD5 hash of the response body (unless some other code has
    already provided an ETag header). If False (the default), the ETag
    will not be automatic.
    
    WARNING: the autotags feature is not designed for URL's which allow
    methods other than GET. For example, if a POST to the same URL returns
    no content, the automatic ETag will be incorrect, breaking a fundamental
    use for entity tags in a possibly destructive fashion. Likewise, if you
    raise 304 Not Modified, the response body will be empty, the ETag hash
    will be incorrect, and your application will break.
    See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.24
    """
    
    # Guard against being run twice.
    if hasattr(response, "ETag"):
        return
    
    status, reason, msg = valid_status(response.status)
    
    etag = response.headers.get('ETag')
    
    # Automatic ETag generation. See warning in docstring.
    if (not etag) and autotags:
        if status == 200:
            etag = response.collapse_body()
            etag = '"%s"' % hashlib.md5.new(etag).hexdigest()
            response.headers['ETag'] = etag
    
    response.ETag = etag
    
    # "If the request would, without the If-Match header field, result in
    # anything other than a 2xx or 412 status, then the If-Match header
    # MUST be ignored."
    if status >= 200 and status <= 299:
        conditions = request.headers.elements('If-Match') or []
        conditions = [str(x) for x in conditions]
        if conditions and not (conditions == ["*"] or etag in conditions):
            return HTTPError(request, response, 412,
                    "If-Match failed: ETag %r did not match %r" % (
                        etag, conditions))
        
        conditions = request.headers.elements('If-None-Match') or []
        conditions = [str(x) for x in conditions]
        if conditions == ["*"] or etag in conditions:
            if request.method in ("GET", "HEAD"):
                return Redirect(request, response, [], 304)
            else:
                return HTTPError(request, response, 412,
                        "If-None-Match failed: ETag %r matched %r" % (
                            etag, conditions))

def validate_since(request, response):
    """Validate the current Last-Modified against If-Modified-Since headers.
    
    If no code has set the Last-Modified response header, then no validation
    will be performed.
    """

    lastmod = response.headers.get('Last-Modified')
    if lastmod:
        status, reason, msg = valid_status(response.status)
        
        since = request.headers.get('If-Unmodified-Since')
        if since and since != lastmod:
            if (status >= 200 and status <= 299) or status == 412:
                return HTTPError(request, response, 412)
        
        since = request.headers.get('If-Modified-Since')
        if since and since == lastmod:
            if (status >= 200 and status <= 299) or status == 304:
                if request.method in ("GET", "HEAD"):
                    return Redirect(request, response, [], 304)
                else:
                    return HTTPError(request, response, 412)

def redirect(request, response, url=''):
    raise Redirect(request, response, url)

def trailing_slash(request, response, missing=True, extra=False):
    """Redirect if request.path has (missing|extra) trailing slash."""

    pi = request.path
    
    if request.index is True:
        if missing:
            if not pi.endswith('/'):
                new_url = url(request, pi + '/', request.qs)
                return Redirect(request, response, new_url)
    elif request.index is False:
        if extra:
            # If pi == '/', don't redirect to ''!
            if pi.endswith('/') and pi != '/':
                new_url = url(request, pi[:-1], request.qs)
                return Redirect(request, response, new_url)
    else:
        return response

def flatten(request, response):
    """Wrap response.body in a generator that recursively iterates over body.
    
    This allows response.body to consist of 'nested generators';
    that is, a set of generators that yield generators.
    """
    def flattener(input):
        for x in input:
            if not isinstance(x, types.GeneratorType):
                yield x
            else:
                for y in flattener(x):
                    yield y 

    response.body = flattener(response.body)
    return response

def check_auth(request, response, users, encrypt=None, realm=None):
    """Check Authentication

    If an authorization header contains credentials, return True, else False.

    @param realm: The authentication realm.
    @type  realm: str

    @param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    @type  users: dict or callable

    @param encrypt: Callable used to encrypt the password returned from
                    the user-agent. if None it defaults to a md5 encryption.
    @type  encrypt: callable
    """

    if 'authorization' in request.headers:
        # make sure the provided credentials are correctly set
        ah = _httpauth.parseAuthorization(request.headers['authorization'])
        if ah is None:
            return HTTPError(request, response, 400)
        
        if not encrypt:
            encrypt = _httpauth.DIGEST_AUTH_ENCODERS[_httpauth.MD5]
        
        if callable(users):
            try:
                # backward compatibility
                users = users() # expect it to return a dictionary

                if not isinstance(users, dict):
                    raise ValueError, "Authentication users must be a dict"
                
                # fetch the user password
                password = users.get(ah["username"], None)
            except TypeError:
                # returns a password (encrypted or clear text)
                password = users(ah["username"])
        else:
            if not isinstance(users, dict):
                raise ValueError, "Authentication users must be a dict"
            
            # fetch the user password
            password = users.get(ah["username"], None)
        
        # validate the authorization by re-computing it here
        # and compare it with what the user-agent provided
        if _httpauth.checkResponse(ah, password, method=request.method,
                                  encrypt=encrypt, realm=realm):
            request.login = ah["username"]
            return True
    
        request.login = False
    return False

def basic_auth(request, response, realm, users, encrypt=None):
    """Perform Basic Authentication
    
    If auth fails, returns an Unauthorized error  with a
    basic authentication header.
    
    @param realm: The authentication realm.
    @type  realm: str

    @param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    @type  users: dict or callable

    @param encrypt: Callable used to encrypt the password returned from
                    the user-agent. if None it defaults to a md5 encryption.
    @type  encrypt: callable
    """

    if check_auth(request, response, users, encrypt):
        return
    
    # inform the user-agent this path is protected
    response.headers["WWW-Authenticate"] = _httpauth.basicAuth(realm)

    return Unauthorized(request, response)
    
def digest_auth(request, response, realm, users):
    """Perform Digest Authentication
    
    If auth fails, raise 401 with a digest authentication header.
    
    @param realm: The authentication realm.
    @type  realm: str

    @param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    @type  users: dict or callable
    """

    if check_auth(request, response, users, realm=realm):
        return
    
    # inform the user-agent this path is protected
    response.headers["WWW-Authenticate"] = _httpauth.digestAuth(realm)
    
    return Unauthorized(request, response)
