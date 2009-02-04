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

import os
import sys
import rfc822
import datetime
from os import getcwd, listdir
from inspect import getargspec
from socket import gethostname
from traceback import format_exc
from os.path import isdir, isfile

from circuits.core import BaseComponent
from circuits import listener, Component
from circuits.lib.sockets import TCPServer

def expose(*channels, **config):
   def decorate(f):
      def wrapper(self, *args, **kwargs):
         if not hasattr(self, "request"):
            self.request, self.response = args[:2]
            self.cookie = self.request.cookie
            args = args[2:]

         try:
            return f(self, *args, **kwargs)
         finally:
            if hasattr(self, "request"):
               del self.request
               del self.response
               del self.cookie
 
      wrapper.type = config.get("type", "listener")
      wrapper.target = config.get("target", None)
      wrapper.channels = channels

      argspec = getargspec(f)
      _args = argspec[0]
      _args.insert(0, "response")
      _args.insert(0, "request")
      varargs = (True if argspec[1] else False)
      varkw = (True if argspec[2] else False)
      if _args and _args[0] == "self":
         del _args[0]

      if _args and _args[0] == "event":
         wrapper.br = 1
      elif _args:
         wrapper.br = 2
      else:
         if varargs and varkw:
            wrapper.br = 2
         elif varkw:
            wrapper.br = 3
         elif varargs:
            wrapper.br = 4
         else:
            wrapper.br = 5

      return wrapper

   return decorate

class ExposeType(type):

    def __init__(cls, name, bases, dct):
        super(ExposeType, cls).__init__(name, bases, dct)

        for name, f in dct.iteritems():
            if callable(f) and not (name[0] == "_" or hasattr(f, "type")):
                setattr(cls, name, expose(name, type="listener")(f))

class Controller(BaseComponent):

    __metaclass__ = ExposeType

    channel = "/"
