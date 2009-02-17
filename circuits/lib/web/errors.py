# Module:   errors
# Date:     11th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Errors

This module implements a set of standard HTTP Errors.
"""

from cgi import escape as _escape
from urlparse import urljoin as _urljoin

import utils
from constants import DEFAULT_ERROR_MESSAGE, RESPONSES, SERVER_VERSION

class BaseError(object):

    def __init__(self, request, response):
        super(BaseError, self).__init__()
        
        self.request = request
        self.response = response

    def __nonzero__(self):
        return False

class HTTPError(BaseError):

    def __init__(self, request, response, status, message=None, error=None):
        super(HTTPError, self).__init__(request, response)

        short, long = RESPONSES.get(status, ("???", "???",))
        message = message or short

        s = DEFAULT_ERROR_MESSAGE % {
            "status": "%s %s" % (status, short),
            "message": _escape(message),
            "traceback": error or "",
            "version": SERVER_VERSION}

        response.clear()
        response.body = s
        response.status = "%s %s" % (status, message)
        response.headers.add_header("Connection", "close")

class Forbidden(HTTPError):

    def __init__(self, request, response, message=None):
        super(Forbidden, self).__init__(request, response, 403, message)

class NotFound(HTTPError):

    def __init__(self, request, response):
        super(NotFound, self).__init__(request, response, 404)

class Redirect(BaseError):

    def __init__(self, request, response, urls, status=None):
        super(Redirect, self).__init__(request, response)

        if isinstance(urls, basestring):
            urls = [urls]
        
        abs_urls = []
        for url in urls:
            # Note that urljoin will "do the right thing" whether url is:
            #  1. a complete URL with host (e.g. "http://www.example.com/test")
            #  2. a URL relative to root (e.g. "/dummy")
            #  3. a URL relative to the current path
            # Note that any query string in request is discarded.
            url = _urljoin(utils.url(request), url)
            abs_urls.append(url)
        urls = abs_urls
        
        # RFC 2616 indicates a 301 response code fits our goal; however,
        # browser support for 301 is quite messy. Do 302/303 instead. See
        # http://ppewww.ph.gla.ac.uk/~flavell/www/post-redirect.html
        if status is None:
            if request.protocol >= (1, 1):
                status = 303
            else:
                status = 302
        else:
            status = int(status)
            if status < 300 or status > 399:
                raise ValueError("status must be between 300 and 399.")
        
        response.status = status
        
        if status in (300, 301, 302, 303, 307):
            response.headers["Content-Type"] = "text/html"
            # "The ... URI SHOULD be given by the Location field
            # in the response."
            response.headers["Location"] = urls[0]
            
            # "Unless the request method was HEAD, the entity of the response
            # SHOULD contain a short hypertext note with a hyperlink to the
            # new URI(s)."
            msg = {300: "This resource can be found at <a href='%s'>%s</a>.",
                   301: "This resource has permanently moved to <a href='%s'>%s</a>.",
                   302: "This resource resides temporarily at <a href='%s'>%s</a>.",
                   303: "This resource can be found at <a href='%s'>%s</a>.",
                   307: "This resource has moved temporarily to <a href='%s'>%s</a>.",
                   }[status]
            response.body = "<br />\n".join([msg % (u, u) for u in urls])
            # Previous code may have set C-L, so we have to reset it
            # (allow finalize to set it).
            response.headers.pop("Content-Length", None)
        elif status == 304:
            # Not Modified.
            # "The response MUST include the following header fields:
            # Date, unless its omission is required by section 14.18.1"
            # The "Date" header should have been set in Response.__init__
            
            # "...the response SHOULD NOT include other entity-headers."
            for key in ("Allow", "Content-Encoding", "Content-Language",
                        "Content-Length", "Content-Location", "Content-MD5",
                        "Content-Range", "Content-Type", "Expires",
                        "Last-Modified"):
                if key in response.headers:
                    del response.headers[key]
            
            # "The 304 response MUST NOT contain a message-body."
            response.body = None
            # Previous code may have set C-L, so we have to reset it.
            response.headers.pop("Content-Length", None)
        elif status == 305:
            # Use Proxy.
            # urls[0] should be the URI of the proxy.
            response.headers["Location"] = urls[0]
            response.body = None
            # Previous code may have set C-L, so we have to reset it.
            response.headers.pop("Content-Length", None)
        else:
            raise ValueError("The %s status code is unknown." % status)
