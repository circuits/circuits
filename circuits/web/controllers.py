"""Controllers

This module implements ...
"""
import json
from functools import update_wrapper
try:
    from collections import Callable
except ImportError:
    from collections.abc import Callable

from circuits.core import BaseComponent, handler
from circuits.tools import getargspec

from . import tools
from .errors import forbidden, httperror, notfound, redirect
from .wrappers import Response


def expose(*channels, **config):
    def decorate(f):
        @handler(*channels, **config)
        def wrapper(self, event, *args, **kwargs):
            try:
                if not hasattr(self, "request"):
                    (self.request, self.response), args = args[:2], args[2:]
                    self.request.args = args
                    self.request.kwargs = kwargs
                    self.cookie = self.request.cookie
                    if hasattr(self.request, "session"):
                        self.session = self.request.session
                if not getattr(f, "event", False):
                    return f(self, *args, **kwargs)
                else:
                    return f(self, event, *args, **kwargs)
            finally:
                if hasattr(self, "request"):
                    del self.request
                    del self.response
                    del self.cookie
                if hasattr(self, "session"):
                    del self.session

        wrapper.args, wrapper.varargs, wrapper.varkw, wrapper.defaults = \
            getargspec(f)
        if wrapper.args and wrapper.args[0] == "self":
            del wrapper.args[0]

        if wrapper.args and wrapper.args[0] == "event":
            f.event = True
            del wrapper.args[0]
        wrapper.event = True

        return update_wrapper(wrapper, f)

    return decorate


class ExposeMetaClass(type):

    def __init__(cls, name, bases, dct):
        super(ExposeMetaClass, cls).__init__(name, bases, dct)

        for k, v in dct.items():
            if isinstance(v, Callable) \
                    and not (k[0] == "_" or hasattr(v, "handler")):
                setattr(cls, k, expose(k)(v))


class BaseController(BaseComponent):

    channel = "/"

    @property
    def uri(self):
        """Return the current Request URI

        .. seealso:: :py:class:`circuits.web.url.URL`
        """

        if hasattr(self, "request"):
            return self.request.uri

    def forbidden(self, description=None):
        """Return a 403 (Forbidden) response

        :param description: Message to display
        :type description: str
        """

        return forbidden(self.request, self.response, description=description)

    def notfound(self, description=None):
        """Return a 404 (Not Found) response

        :param description: Message to display
        :type description: str
        """

        return notfound(self.request, self.response, description=description)

    def redirect(self, urls, code=None):
        """Return a 30x (Redirect) response

        Redirect to another location specified by urls with an optional
        custom response code.

        :param urls: A single URL or list of URLs
        :type urls: str or list

        :param code: HTTP Redirect code
        :type code: int
        """
        return redirect(self.request, self.response, urls, code=code)

    def serve_file(self, path, type=None, disposition=None, name=None):
        return tools.serve_file(
            self.request, self.response, path, type, disposition, name
        )

    def serve_download(self, path, name=None):
        return tools.serve_download(
            self.request, self.response, path, name
        )

    def expires(self, secs=0, force=False):
        tools.expires(self.request, self.response, secs, force)


Controller = ExposeMetaClass("Controller", (BaseController,), {})


def exposeJSON(*channels, **config):
    def decorate(f):
        @handler(*channels, **config)
        def wrapper(self, *args, **kwargs):
            try:
                if not hasattr(self, "request"):
                    self.request, self.response = args[:2]
                    args = args[2:]
                    self.cookie = self.request.cookie
                    if hasattr(self.request, "session"):
                        self.session = self.request.session
                self.response.headers["Content-Type"] = "application/json"
                result = f(self, *args, **kwargs)
                if (isinstance(result, httperror) or isinstance(result, Response)):
                    return result
                else:
                    return json.dumps(result)
            finally:
                if hasattr(self, "request"):
                    del self.request
                    del self.response
                    del self.cookie
                if hasattr(self, "session"):
                    del self.session

        wrapper.args, wrapper.varargs, wrapper.varkw, wrapper.defaults = \
            getargspec(f)
        if wrapper.args and wrapper.args[0] == "self":
            del wrapper.args[0]

        return update_wrapper(wrapper, f)

    return decorate


class ExposeJSONMetaClass(type):

    def __init__(cls, name, bases, dct):
        super(ExposeJSONMetaClass, cls).__init__(name, bases, dct)

        for k, v in dct.items():
            if isinstance(v, Callable) \
                    and not (k[0] == "_" or hasattr(v, "handler")):
                setattr(cls, k, exposeJSON(k)(v))


JSONController = ExposeJSONMetaClass("JSONController", (BaseController,), {})
