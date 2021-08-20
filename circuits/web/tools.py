"""Tools

This module implements tools used throughout circuits.web.
These tools can also be used within Controlelrs and request handlers.
"""
import hashlib
import mimetypes
import os
import stat
from datetime import datetime, timedelta
from email.generator import _make_boundary
from email.utils import formatdate
from time import mktime
try:
    from collections import Callable
except ImportError:
    from collections.abc import Callable

from circuits import BaseComponent, handler
from circuits.web.wrappers import Host

from . import _httpauth
from .errors import httperror, notfound, redirect, unauthorized
from .utils import compress, get_ranges

mimetypes.init()
mimetypes.add_type("image/x-dwg", ".dwg")
mimetypes.add_type("image/x-icon", ".ico")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/xhtml+xml", ".xhtml")


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
        if isinstance(secs, timedelta):
            secs = (86400 * secs.days) + secs.seconds

        if secs == 0:
            if force or "Pragma" not in headers:
                headers["Pragma"] = "no-cache"
            if request.protocol >= (1, 1):
                if force or "Cache-Control" not in headers:
                    headers["Cache-Control"] = "no-cache, must-revalidate"
            # Set an explicit Expires date in the past.
            now = datetime.now()
            lastyear = now.replace(year=now.year - 1)
            expiry = formatdate(
                mktime(lastyear.timetuple()), usegmt=True
            )
        else:
            expiry = formatdate(response.time + secs, usegmt=True)
        if force or "Expires" not in headers:
            headers["Expires"] = expiry


def serve_file(request, response, path, type=None, disposition=None,
               name=None):
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
        return notfound(request, response)

    # Check if path is a directory.
    if stat.S_ISDIR(st.st_mode):
        # Let the caller deal with it as they like.
        return notfound(request, response)

    # Set the Last-Modified response header, so that
    # modified-since validation code can work.
    response.headers['Last-Modified'] = formatdate(
        st.st_mtime, usegmt=True
    )

    result = validate_since(request, response)
    if result is not None:
        return result

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
            return httperror(request, response, 416)
        if r:
            if len(r) == 1:
                # Return a single-part response.
                start, stop = r[0]
                r_len = stop - start
                response.status = 206
                response.headers['Content-Range'] = (
                    "bytes %s-%s/%s" % (start, stop - 1, c_len)
                )
                response.headers['Content-Length'] = r_len
                bodyfile.seek(start)
                response.body = bodyfile.read(r_len)
            else:
                # Return a multipart/byteranges response.
                response.status = 206
                boundary = _make_boundary()
                ct = "multipart/byteranges; boundary=%s" % boundary
                response.headers['Content-Type'] = ct
                if "Content-Length" in response.headers:
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

    status = response.status

    etag = response.headers.get('ETag')

    # Automatic ETag generation. See warning in docstring.
    if (not etag) and autotags:
        if status == 200:
            etag = response.collapse_body()
            etag = '"%s"' % hashlib.new('md5', etag).hexdigest()
            response.headers['ETag'] = etag

    response.ETag = etag

    # "If the request would, without the If-Match header field, result in
    # anything other than a 2xx or 412 status, then the If-Match header
    # MUST be ignored."
    if status >= 200 and status <= 299:
        conditions = request.headers.elements('If-Match') or []
        conditions = [str(x) for x in conditions]
        if conditions and not (conditions == ["*"] or etag in conditions):
            return httperror(
                request, response, 412,
                description="If-Match failed: ETag %r did not match %r" % (
                    etag, conditions
                )
            )

        conditions = request.headers.elements('If-None-Match') or []
        conditions = [str(x) for x in conditions]
        if conditions == ["*"] or etag in conditions:
            if request.method in ("GET", "HEAD"):
                return redirect(request, response, [], code=304)
            else:
                return httperror(
                    request, response, 412,
                    description=(
                        "If-None-Match failed: ETag %r matched %r" % (
                            etag, conditions
                        )
                    )
                )


def validate_since(request, response):
    """Validate the current Last-Modified against If-Modified-Since headers.

    If no code has set the Last-Modified response header, then no validation
    will be performed.
    """

    lastmod = response.headers.get('Last-Modified')
    if lastmod:
        status = response.status

        since = request.headers.get('If-Unmodified-Since')
        if since and since != lastmod:
            if (status >= 200 and status <= 299) or status == 412:
                return httperror(request, response, 412)

        since = request.headers.get('If-Modified-Since')
        if since and since == lastmod:
            if (status >= 200 and status <= 299) or status == 304:
                if request.method in ("GET", "HEAD"):
                    return redirect(request, response, [], code=304)
                else:
                    return httperror(request, response, 412)


def check_auth(request, response, realm, users, encrypt=None):
    """Check Authentication

    If an Authorization header contains credentials, return True, else False.

    :param realm: The authentication realm.
    :type  realm: str

    :param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    :type  users: dict or callable

    :param encrypt: Callable used to encrypt the password returned from
                    the user-agent. if None it defaults to a md5 encryption.
    :type  encrypt: callable
    """

    if "Authorization" in request.headers:
        # make sure the provided credentials are correctly set
        ah = _httpauth.parseAuthorization(request.headers.get("Authorization"))
        if ah is None:
            return httperror(request, response, 400)

        if not encrypt:
            encrypt = _httpauth.DIGEST_AUTH_ENCODERS[_httpauth.MD5]

        if isinstance(users, Callable):
            try:
                # backward compatibility
                users = users()  # expect it to return a dictionary

                if not isinstance(users, dict):
                    raise ValueError("Authentication users must be a dict")

                # fetch the user password
                password = users.get(ah["username"], None)
            except TypeError:
                # returns a password (encrypted or clear text)
                password = users(ah["username"])
        else:
            if not isinstance(users, dict):
                raise ValueError("Authentication users must be a dict")

            # fetch the user password
            password = users.get(ah["username"], None)

        # validate the Authorization by re-computing it here
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

    :param realm: The authentication realm.
    :type  realm: str

    :param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    :type  users: dict or callable

    :param encrypt: Callable used to encrypt the password returned from
                    the user-agent. if None it defaults to a md5 encryption.
    :type  encrypt: callable
    """

    if check_auth(request, response, realm, users, encrypt):
        return

    # inform the user-agent this path is protected
    response.headers["WWW-Authenticate"] = _httpauth.basicAuth(realm)

    return unauthorized(request, response)


def digest_auth(request, response, realm, users):
    """Perform Digest Authentication

    If auth fails, raise 401 with a digest authentication header.

    :param realm: The authentication realm.
    :type  realm: str

    :param users: A dict of the form: {username: password} or a callable
                  returning a dict.
    :type  users: dict or callable
    """

    if check_auth(request, response, realm, users):
        return

    # inform the user-agent this path is protected
    response.headers["WWW-Authenticate"] = _httpauth.digestAuth(realm)

    return unauthorized(request, response)


def gzip(response, level=4, mime_types=("text/html", "text/plain",)):
    """Try to gzip the response body if Content-Type in mime_types.

    response.headers['Content-Type'] must be set to one of the
    values in the mime_types arg before calling this function.

    No compression is performed if any of the following hold:
        * The client sends no Accept-Encoding request header
        * No 'gzip' or 'x-gzip' is present in the Accept-Encoding header
        * No 'gzip' or 'x-gzip' with a qvalue > 0 is present
        * The 'identity' value is given with a qvalue > 0.
    """

    if not response.body:
        # Response body is empty (might be a 304 for instance)
        return response

    # If returning cached content (which should already have been gzipped),
    # don't re-zip.
    if getattr(response.request, "cached", False):
        return response

    acceptable = response.request.headers.elements('Accept-Encoding')
    if not acceptable:
        # If no Accept-Encoding field is present in a request,
        # the server MAY assume that the client will accept any
        # content coding. In this case, if "identity" is one of
        # the available content-codings, then the server SHOULD use
        # the "identity" content-coding, unless it has additional
        # information that a different content-coding is meaningful
        # to the client.
        return response

    ct = response.headers.get('Content-Type', 'text/html').split(';')[0]
    for coding in acceptable:
        if coding.value == 'identity' and coding.qvalue != 0:
            return response
        if coding.value in ('gzip', 'x-gzip'):
            if coding.qvalue == 0:
                return response
            if ct in mime_types:
                # Return a generator that compresses the page
                varies = response.headers.get("Vary", "")
                varies = [x.strip() for x in varies.split(",") if x.strip()]
                if "Accept-Encoding" not in varies:
                    varies.append("Accept-Encoding")
                response.headers['Vary'] = ", ".join(varies)

                response.headers['Content-Encoding'] = 'gzip'
                response.body = compress(response.body, level)
                if "Content-Length" in response.headers:
                    # Delete Content-Length header so finalize() recalcs it.
                    del response.headers["Content-Length"]
            return response
    return httperror(
        response.request, response, 406, description="identity, gzip"
    )


class ReverseProxy(BaseComponent):

    headers = ('X-Real-IP', 'X-Forwarded-For')

    def init(self, headers=None):
        """Web Component for identifying the original client IP when a reverse proxy is used

        :param headers: List of HTTP headers to read the original client IP
        """

        if headers:
            self.headers = headers

    @handler('request', priority=1)
    def _on_request(self, req, *_):
        ip = [v for v in map(req.headers.get, self.headers) if v]
        req.remote = ip and Host(ip[0], "", ip[0]) or req.remote
