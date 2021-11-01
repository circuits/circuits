"""
Tools

This module implements tools used throughout circuits.web.
These tools can also be used within Controllers and request handlers.
"""

import hashlib
import mimetypes
import os
import stat
from collections.abc import Callable
from datetime import datetime, timedelta

import httoop

from circuits import BaseComponent, handler
from circuits.web.wrappers import Host

from . import _httpauth
from .errors import httperror, notfound, redirect, unauthorized


mimetypes.init()
mimetypes.add_type('image/x-dwg', '.dwg')
mimetypes.add_type('image/x-icon', '.ico')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('application/xhtml+xml', '.xhtml')


def expires(request, response, secs=0, force=False):
    """
    Tool for influencing cache mechanisms using the 'Expires' header.

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
            secs = secs.total_seconds()

        if secs == 0:
            if force or 'Pragma' not in headers:
                headers['Pragma'] = 'no-cache'
            if request.protocol >= (1, 1):
                if force or 'Cache-Control' not in headers:
                    headers['Cache-Control'] = 'no-cache, must-revalidate'
            # Set an explicit Expires date in the past.
            now = datetime.utcnow()
            lastyear = now.replace(year=now.year - 1)
            expiry = httoop.Date(lastyear)
        else:
            expiry = httoop.Date(response.time + secs)
        if force or 'Expires' not in headers:
            headers['Expires'] = str(expiry)


def serve_file(request, response, path, type=None, disposition=None, name=None):
    """
    Set status, headers, and body in order to serve the given file.

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
    response.headers['Last-Modified'] = str(httoop.Date(st.st_mtime))

    result = validate_since(request, response)
    if result is not None:
        return result

    if type is None:
        # Set content-type based on filename extension
        ext = os.path.splitext(path)[-1].lower()
        type = mimetypes.types_map.get(ext, 'text/plain')
    response.headers['Content-Type'] = type

    if disposition is not None:
        if name is None:
            name = os.path.basename(path)
        cd = f'{disposition}; filename="{name}"'
        response.headers['Content-Disposition'] = cd

    # Set Content-Length and use an iterable (file object)
    #   this way CP won't load the whole file in memory
    c_len = st.st_size
    bodyfile = open(path, 'rb')

    response.headers['Accept-Ranges'] = 'bytes'

    req = request.to_httoop()
    res = response.to_httoop()
    res.body = bodyfile
    from httoop.semantic.response import ComposedResponse

    c = ComposedResponse(res, req)
    if not c.prepare_ranges():
        if res.status == 416:
            return httperror(request, response, 416)
        response.headers['Content-Length'] = c_len
        response.body = bodyfile
        return response

    response.status = res.status
    if 'Content-Range' in res.headers:
        response.headers['Content-Range'] = res.headers['Content-Range']
    if 'Content-Type' in res.headers:
        response.headers['Content-Type'] = res.headers['Content-Type']
    if 'Content-Length' in res.headers:
        response.headers['Content-Length'] = res.headers['Content-Length']
    response.body = res.body.fd
    return response


def serve_download(request, response, path, name=None):
    """Serve 'path' as an application/x-download attachment."""
    type = 'application/x-download'
    disposition = 'attachment'

    return serve_file(request, response, path, type, disposition, name)


def validate_etags(request, response, autotags=False):
    """
    Validate the current ETag against If-Match, If-None-Match headers.

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
    if hasattr(response, 'ETag'):
        return

    res = response.to_httoop()
    req = response.request.to_httoop()
    status = res.status

    etag = response.headers.get('ETag')

    # Automatic ETag generation. See warning in docstring.
    if not etag and autotags:
        if status == 200:
            etag = bytes(response)
            etag = '"%s"' % hashlib.new('md5', etag).hexdigest()
            response.headers['ETag'] = etag

    response.ETag = etag

    # "If the request would, without the If-Match header field, result in
    # anything other than a 2xx or 412 status, then the If-Match header
    # MUST be ignored."
    if status.successful:
        if 'If-Match' in req.headers and not any(condition.matches(etag) for condition in req.headers.elements('If-Match')):
            return httperror(
                request,
                response,
                412,
                description='If-Match failed: ETag %r did not match %r' % (etag, req.headers['If-Match']),
            )

        if 'If-None-Match' in req.headers and any(
            condition.matches(etag) for condition in req.headers.elements('If-None-Match')
        ):
            if request.method in ('GET', 'HEAD'):
                return redirect(request, response, [], code=304)
            else:
                return httperror(
                    request,
                    response,
                    412,
                    description=('If-None-Match failed: ETag %r matched %r' % (etag, req.headers['If-None-Match'])),
                )


def validate_since(request, response):
    """
    Validate the current Last-Modified against If-Modified-Since headers.

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
                if request.method in ('GET', 'HEAD'):
                    return redirect(request, response, [], code=304)
                else:
                    return httperror(request, response, 412)


def check_auth(request, response, realm, users, encrypt=None):
    """
    Check Authentication

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
    if 'Authorization' in request.headers:
        # make sure the provided credentials are correctly set
        ah = _httpauth.parseAuthorization(request.headers.get('Authorization'))
        if ah is None:
            return httperror(request, response, 400)

        if not encrypt:
            encrypt = _httpauth.DIGEST_AUTH_ENCODERS[_httpauth.MD5]

        if isinstance(users, Callable):
            try:
                # backward compatibility
                users = users()  # expect it to return a dictionary

                if not isinstance(users, dict):
                    raise ValueError('Authentication users must be a dict')

                # fetch the user password
                password = users.get(ah['username'], None)
            except TypeError:
                # returns a password (encrypted or clear text)
                password = users(ah['username'])
        else:
            if not isinstance(users, dict):
                raise ValueError('Authentication users must be a dict')

            # fetch the user password
            password = users.get(ah['username'], None)

        # validate the Authorization by re-computing it here
        # and compare it with what the user-agent provided
        if _httpauth.checkResponse(ah, password, method=request.method, encrypt=encrypt, realm=realm):
            request.login = ah['username']
            return True

        request.login = False
    return False


def basic_auth(request, response, realm, users, encrypt=None):
    """
    Perform Basic Authentication

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
    response.headers['WWW-Authenticate'] = _httpauth.basicAuth(realm)

    return unauthorized(request, response)


def digest_auth(request, response, realm, users):
    """
    Perform Digest Authentication

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
    response.headers['WWW-Authenticate'] = _httpauth.digestAuth(realm)

    return unauthorized(request, response)


def gzip(
    response,
    level=4,
    mime_types=(
        'text/html',
        'text/plain',
    ),
):
    """
    Try to gzip the response body if Content-Type in mime_types.

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
    if getattr(response.request, 'cached', False):
        return response

    acceptable = response.request.to_httoop().headers.elements('Accept-Encoding')
    if not acceptable:
        # If no Accept-Encoding field is present in a request,
        # the server MAY assume that the client will accept any
        # content coding. In this case, if "identity" is one of
        # the available content-codings, then the server SHOULD use
        # the "identity" content-coding, unless it has additional
        # information that a different content-coding is meaningful
        # to the client.
        return response

    res = response.to_httoop()
    ct = res.headers.element('Content-Type')
    ct = ct.value if ct else 'text/html'
    if ct not in mime_types:
        return response

    for coding in acceptable:
        if not coding.quality:
            continue
        if coding.value == 'identity':
            return response
        if coding.value in ('gzip', 'x-gzip'):
            # Return a generator that compresses the page
            if 'Accept-Encoding' not in res.headers.elements('Vary'):
                res.headers.append_element('Vary', 'Accept-Encoding')
                response.headers['Vary'] = res.headers['Vary']

            response.headers['Content-Encoding'] = coding.value
            res.body.content_encoding = 'gzip; level=%d' % (level,)
            response.body = res.body.__iter__()
            # Delete Content-Length header so finalize() recalcs it.
            response.headers.pop('Content-Length', None)
            return response
    return httperror(response.request, response, 406, description='identity, gzip')


class ReverseProxy(BaseComponent):
    headers = ('X-Real-IP', 'X-Forwarded-For')

    def init(self, headers=None):
        """
        Web Component for identifying the original client IP when a reverse proxy is used

        :param headers: List of HTTP headers to read the original client IP
        """
        if headers:
            self.headers = headers

    @handler('request', priority=1)
    def _on_request(self, req, *_):
        ip = [v for v in map(req.headers.get, self.headers) if v]
        req.remote = ip and Host(ip[0], '', ip[0]) or req.remote
