# Module:   core
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core Web Components

This module implements Core Web Components that can be used to build
web applications and web systems, be it an AJAX backend, a RESTful
server or a website. These Components offer a full featured web
server implementation with support for headers, cookies, positional
and keyword arguments, filtering, url dispatching and more.
"""

from inspect import getargspec
from functools import update_wrapper

from circuits.core import handler, BaseComponent

import tools
from errors import Forbidden, NotFound, Redirect

def expose(*channels, **config):
   def decorate(f):
      @handler(*channels, **config)
      def wrapper(self, *args, **kwargs):
         try:
            if not hasattr(self, "request"):
                (self.request, self.response), args = args[:2], args[2:]
                self.cookie = self.request.cookie
                if hasattr(self.request, "session"):
                   self.session = self.request.session
            return f(self, *args, **kwargs)
         finally:
            if hasattr(self, "request"):
               del self.request
               del self.response
               del self.cookie
            if hasattr(self, "session"):
               del self.session
 
      wrapper.varargs = getargspec(f)[1]

      return update_wrapper(wrapper, f)

   return decorate

class ExposeType(type):

    def __init__(cls, name, bases, dct):
        super(ExposeType, cls).__init__(name, bases, dct)

        for k, v in dct.iteritems():
            if callable(v) and not (k[0] == "_" or hasattr(v, "handler")):
                setattr(cls, k, expose(k)(v))

class BaseController(BaseComponent):

    channel = "/"

    def forbidden(self, message=None):
        return Forbidden(self.request, self.response, message)

    def notfound(self, message=None):
       return NotFound(self.request, self.response, message)

    def redirect(self, urls, status=None):
       return Redirect(self.request, self.response, urls, status)

    def serve_file(self, path, type=None, disposition=None, name=None):
        return tools.serve_file(self.request, self.response, path,
                type, disposition, name)

    def serve_download(self, path, name=None):
        return tools.serve_download(self.request, self.response, path,
                name)

    def expires(self, secs=0, force=False):
        return tools.expires(self.request, self.response, secs, force)

class Controller(BaseController):

    __metaclass__ = ExposeType
