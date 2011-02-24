# Module:   controllers
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Controllers

This module implements ...
"""

from inspect import getargspec
from functools import update_wrapper

try:
    import json
    HAS_JSON = 2
except ImportError:
    try:
        import simplejson as json
        HAS_JSON = 1
    except ImportError:
        import warnings
        HAS_JSON = 0
        warnings.warn("No json support available.")

from circuits.core import handler, BaseComponent

import tools
from errors import Forbidden, NotFound, Redirect

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
      wrapper.event = True

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

    def url(self, *args, **kwargs):
        return self.request.url(*args, **kwargs)

    def forbidden(self, description=None):
        return Forbidden(self.request, self.response, description=description)

    def notfound(self, description=None):
       return NotFound(self.request, self.response, description=description)

    def redirect(self, urls, code=None):
       return Redirect(self.request, self.response, urls, code=code)

    def serve_file(self, path, type=None, disposition=None, name=None):
        return tools.serve_file(self.request, self.response, path,
                type, disposition, name)

    def serve_download(self, path, name=None):
        return tools.serve_download(self.request, self.response, path,
                name)

    def expires(self, secs=0, force=False):
        tools.expires(self.request, self.response, secs, force)

class Controller(BaseController):

    __metaclass__ = ExposeType

if HAS_JSON:

    def exposeJSON(*channels, **config):
       def decorate(f):
          @handler(*channels, **config)
          def wrapper(self, *args, **kwargs):
             try:
                if not hasattr(self, "request"):
                    (self.request, self.response), args = args[:2], args[2:]
                    self.cookie = self.request.cookie
                    if hasattr(self.request, "session"):
                       self.session = self.request.session
                self.response.headers["Content-Type"] = "application/json"
                return json.dumps(f(self, *args, **kwargs))
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

    class ExposeJSONType(type):

        def __init__(cls, name, bases, dct):
            super(ExposeJSONType, cls).__init__(name, bases, dct)

            for k, v in dct.iteritems():
                if callable(v) and not (k[0] == "_" or hasattr(v, "handler")):
                    setattr(cls, k, exposeJSON(k)(v))


    class JSONController(BaseController):

        __metaclass__ = ExposeJSONType
