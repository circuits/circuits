"""Exceptions

This module implements a set of standard HTTP Errors as Python Exceptions.

Note: This code is mostly borrowed from werkzeug and adapted for circuits.web
"""
from inspect import isclass

from .constants import HTTP_STATUS_CODES


class HTTPException(Exception):

    """
    Baseclass for all HTTP exceptions.  This exception can be called by WSGI
    applications to render a default error page or you can catch the subclasses
    of it independently and render nicer error messages.
    """

    code = None
    traceback = True
    description = None

    def __init__(self, description=None, traceback=None):
        super(HTTPException, self).__init__("%d %s" % (self.code, self.name))
        if description is not None:
            self.description = description
        if traceback is not None:
            self.traceback = traceback

    @property
    def name(self):
        """The status name."""
        return HTTP_STATUS_CODES.get(self.code, '')

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))


class BadRequest(HTTPException):

    """*400* `Bad Request`

    Raise if the browser sends something to the application the application
    or server cannot handle.
    """
    code = 400
    description = (
        '<p>The browser (or proxy) sent a request that this server could '
        'not understand.</p>'
    )


class UnicodeError(HTTPException):

    """
    raised by the request functions if they were unable to decode the
    incoming data properly.
    """


class Unauthorized(HTTPException):

    """*401* `Unauthorized`

    Raise if the user is not authorized.  Also used if you want to use HTTP
    basic auth.
    """
    code = 401
    description = (
        '<p>The server could not verify that you are authorized to access '
        'the URL requested.  You either supplied the wrong credentials (e.g. '
        'a bad password), or your browser doesn\'t understand how to supply '
        'the credentials required.</p><p>In case you are allowed to request '
        'the document, please check your user-id and password and try '
        'again.</p>'
    )


class Forbidden(HTTPException):

    """*403* `Forbidden`

    Raise if the user doesn't have the permission for the requested resource
    but was authenticated.
    """
    code = 403
    description = (
        '<p>You don\'t have the permission to access the requested resource. '
        'It is either read-protected or not readable by the server.</p>'
    )


class NotFound(HTTPException):

    """*404* `Not Found`

    Raise if a resource does not exist and never existed.
    """
    code = 404
    description = (
        '<p>The requested URL was not found on the server.</p>'
        '<p>If you entered the URL manually please check your spelling and '
        'try again.</p>'
    )


class MethodNotAllowed(HTTPException):

    """*405* `Method Not Allowed`

    Raise if the server used a method the resource does not handle.  For
    example `POST` if the resource is view only.  Especially useful for REST.

    The first argument for this exception should be a list of allowed methods.
    Strictly speaking the response would be invalid if you don't provide valid
    methods in the header which you can do with that list.
    """
    code = 405

    def __init__(self, method, description=None):
        HTTPException.__init__(self, description)
        if description is None:
            self.description = (
                '<p>The method %s is not allowed '
                'for the requested URL.</p>'
            ) % method


class NotAcceptable(HTTPException):

    """*406* `Not Acceptable`

    Raise if the server can't return any content conforming to the
    `Accept` headers of the client.
    """
    code = 406

    description = (
        '<p>The resource identified by the request is only capable of '
        'generating response entities which have content characteristics '
        'not acceptable according to the accept headers sent in the '
        'request.</p>'
    )


class RequestTimeout(HTTPException):

    """*408* `Request Timeout`

    Raise to signalize a timeout.
    """
    code = 408
    description = (
        '<p>The server closed the network connection because the browser '
        'didn\'t finish the request within the specified time.</p>'
    )


class Gone(HTTPException):

    """*410* `Gone`

    Raise if a resource existed previously and went away without new location.
    """
    code = 410
    description = (
        '<p>The requested URL is no longer available on this server and '
        'there is no forwarding address.</p><p>If you followed a link '
        'from a foreign page, please contact the author of this page.'
    )


class LengthRequired(HTTPException):

    """*411* `Length Required`

    Raise if the browser submitted data but no ``Content-Length`` header which
    is required for the kind of processing the server does.
    """
    code = 411
    description = (
        '<p>A request with this method requires a valid <code>Content-'
        'Length</code> header.</p>'
    )


class PreconditionFailed(HTTPException):

    """*412* `Precondition Failed`

    Status code used in combination with ``If-Match``, ``If-None-Match``, or
    ``If-Unmodified-Since``.
    """
    code = 412
    description = (
        '<p>The precondition on the request for the URL failed positive '
        'evaluation.</p>'
    )


class RequestEntityTooLarge(HTTPException):

    """*413* `Request Entity Too Large`

    The status code one should return if the data submitted exceeded a given
    limit.
    """
    code = 413
    description = (
        '<p>The data value transmitted exceeds the capacity limit.</p>'
    )


class RequestURITooLarge(HTTPException):

    """*414* `Request URI Too Large`

    Like *413* but for too long URLs.
    """
    code = 414
    description = (
        '<p>The length of the requested URL exceeds the capacity limit '
        'for this server.  The request cannot be processed.</p>'
    )


class UnsupportedMediaType(HTTPException):

    """*415* `Unsupported Media Type`

    The status code returned if the server is unable to handle the media type
    the client transmitted.
    """
    code = 415
    description = (
        '<p>The server does not support the media type transmitted in '
        'the request.</p>'
    )


class RangeUnsatisfiable(HTTPException):

    """*416* `Range Unsatisfiable`

    The status code returned if the server is unable to satisfy the request range
    """

    code = 416
    description = (
        '<p>The server cannot satisfy the request range(s).</p>'
    )


class InternalServerError(HTTPException):

    """*500* `Internal Server Error`

    Raise if an internal server error occurred.  This is a good fallback if an
    unknown error occurred in the dispatcher.
    """
    code = 500
    description = (
        '<p>The server encountered an internal error and was unable to '
        'complete your request.  Either the server is overloaded or there '
        'is an error in the application.</p>'
    )


class NotImplemented(HTTPException):

    """*501* `Not Implemented`

    Raise if the application does not support the action requested by the
    browser.
    """
    code = 501
    description = (
        '<p>The server does not support the action requested by the '
        'browser.</p>'
    )


class BadGateway(HTTPException):

    """*502* `Bad Gateway`

    If you do proxying in your application you should return this status code
    if you received an invalid response from the upstream server it accessed
    in attempting to fulfill the request.
    """
    code = 502
    description = (
        '<p>The proxy server received an invalid response from an upstream '
        'server.</p>'
    )


class ServiceUnavailable(HTTPException):

    """*503* `Service Unavailable`

    Status code you should return if a service is temporarily unavailable.
    """
    code = 503
    description = (
        '<p>The server is temporarily unable to service your request due to '
        'maintenance downtime or capacity problems.  Please try again '
        'later.</p>'
    )


class Redirect(HTTPException):

    code = 303

    def __init__(self, urls, status=None):
        super(Redirect, self).__init__()

        if isinstance(urls, str):
            self.urls = [urls]
        else:
            self.urls = urls

        self.status = status


__all__ = [
    x[0] for x in list(globals().items())
    if isclass(x[1]) and issubclass(x[1], HTTPException)
]
