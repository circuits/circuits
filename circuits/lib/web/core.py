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

from circuits.core import BaseComponent

from errors import Forbidden, NotFound, Redirect

def expose(*channels, **config):
   def decorate(f):
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
 
      wrapper.type = config.get("type", "listener")
      wrapper.target = config.get("target", None)
      wrapper.channels = channels

      _argspec = getargspec(f)
      _args = _argspec[0]
      _args.insert(0, "response")
      _args.insert(0, "request")
      if _args and _args[0] == "self":
         del _args[0]
      if _args and _args[0] == "event":
         wrapper._passEvent = True
      else:
         wrapper._passEvent = False

      return update_wrapper(wrapper, f)

   return decorate

class ExposeType(type):

    def __init__(cls, name, bases, dct):
        super(ExposeType, cls).__init__(name, bases, dct)

        for name, f in dct.iteritems():
            if callable(f) and not (name[0] == "_" or hasattr(f, "type")):
                setattr(cls, name, expose(name, type="listener")(f))

class BaseController(BaseComponent):

    channel = "/"

    def forbidden(self, message=None):
        return Forbidden(self.request, self.response, message)

    def notfound(self, message=None):
       return NotFound(self.request, self.response, message)

    def redirect(self, urls, status=None):
       return Redirect(self.request, self.response, urls, status)

class Controller(BaseController):

    __metaclass__ = ExposeType
