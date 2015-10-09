# Module:   errors
# Date:     11th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Errors

This module implements a set of standard HTTP Errors.
"""

from cgi import escape

try:
    from urllib.parse import urljoin as _urljoin
except ImportError:
    from urlparse import urljoin as _urljoin  # NOQA

from circuits import Event

from ..six import string_types
from .constants import SERVER_URL, SERVER_VERSION
from .constants import DEFAULT_ERROR_MESSAGE, HTTP_STATUS_CODES


class httpevent(Event):
    """An event for signaling an HTTP special condition"""

    code = 500
    description = ""
    contenttype = "text/html"

    def __init__(self, request, response, code=None, **kwargs):
        """
        The constructor creates a new instance and modifies the *response*
        argument to reflect the error.
        """
        super(httpevent, self).__init__(request, response, code, **kwargs)

        # Override HTTPError subclasses
        self.name = "httperror"

        self.request = request
        self.response = response

        if code is not None:
            self.code = code

        self.error = kwargs.get("error", None)

        self.description = kwargs.get(
            "description", getattr(self.__class__, "description", "")
        )

        if self.error is not None:
            self.traceback = "ERROR: (%s) %s\n%s" % (
                self.error[0], self.error[1], "".join(self.error[2])
            )
        else:
            self.traceback = ""

        self.response.close = True
        self.response.status = self.code

        self.response.headers["Content-Type"] = self.contenttype

        self.data = {
            "code": self.code,
            "name": HTTP_STATUS_CODES.get(self.code, "???"),
            "description": self.description,
            "traceback": escape(self.traceback),
            "url": SERVER_URL,
            "version": SERVER_VERSION
        }

    def sanitize(self):
        if self.code != 201 and not (299 < self.code < 400):
            if "Location" in self.response.headers:
                del self.response.headers["Location"]

    def __str__(self):
        self.sanitize()
        return DEFAULT_ERROR_MESSAGE % self.data

    def __repr__(self):
        return "<%s %d %s>" % (
            self.__class__.__name__, self.code, HTTP_STATUS_CODES.get(
                self.code, "???"
            )
        )


class httperror(httpevent):
    """An event for signaling an HTTP error"""


class forbidden(httperror):
    """An event for signaling the HTTP Forbidden error"""

    code = 403


class unauthorized(httperror):
    """An event for signaling the HTTP Unauthorized error"""

    code = 401


class notfound(httperror):
    """An event for signaling the HTTP Not Fouond error"""

    code = 404


class redirect(httpevent):
    """An event for signaling the HTTP Redirect response"""

    def __init__(self, request, response, urls, code=None):
        """
        The constructor creates a new instance and modifies the
        *response* argument to reflect a redirect response to the
        given *url*.
        """

        if isinstance(urls, string_types):
            urls = [urls]

        abs_urls = []
        for url in urls:
            # Note that urljoin will "do the right thing" whether url is:
            #  1. a complete URL with host (e.g. "http://www.example.com/test")
            #  2. a URL relative to root (e.g. "/dummy")
            #  3. a URL relative to the current path
            # Note that any query string in request is discarded.
            url = request.uri.relative(url).unicode()
            abs_urls.append(url)
        self.urls = urls = abs_urls

        # RFC 2616 indicates a 301 response code fits our goal; however,
        # browser support for 301 is quite messy. Do 302/303 instead. See
        # http://ppewww.ph.gla.ac.uk/~flavell/www/post-redirect.html
        if code is None:
            if request.protocol >= (1, 1):
                code = 303
            else:
                code = 302
        else:
            if code < 300 or code > 399:
                raise ValueError("status code must be between 300 and 399.")

        super(redirect, self).__init__(request, response, code)

        if code in (300, 301, 302, 303, 307):
            response.headers["Content-Type"] = "text/html"
            # "The ... URI SHOULD be given by the Location field
            # in the response."
            response.headers["Location"] = urls[0]

            # "Unless the request method was HEAD, the entity of the response
            # SHOULD contain a short hypertext note with a hyperlink to the
            # new URI(s)."
            msg = {300: "This resource can be found at <a href='%s'>%s</a>.",
                   301: ("This resource has permanently moved to "
                         "<a href='%s'>%s</a>."),
                   302: ("This resource resides temporarily at "
                         "<a href='%s'>%s</a>."),
                   303: ("This resource can be found at "
                         "<a href='%s'>%s</a>."),
                   307: ("This resource has moved temporarily to "
                         "<a href='%s'>%s</a>."),
                   }[code]
            response.body = "<br />\n".join([msg % (u, u) for u in urls])
            # Previous code may have set C-L, so we have to reset it
            # (allow finalize to set it).
            response.headers.pop("Content-Length", None)
        elif code == 304:
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
        elif code == 305:
            # Use Proxy.
            # urls[0] should be the URI of the proxy.
            response.headers["Location"] = urls[0]
            response.body = None
            # Previous code may have set C-L, so we have to reset it.
            response.headers.pop("Content-Length", None)
        else:
            raise ValueError("The %s status code is unknown." % code)

    def __repr__(self):
        if len(self.channels) > 1:
            channels = repr(self.channels)
        elif len(self.channels) == 1:
            channels = str(self.channels[0])
        else:
            channels = ""
        return "<%s %d[%s.%s] %s>" % (
            self.__class__.__name__, self.code, channels, self.name,
            " ".join(self.urls)
        )
