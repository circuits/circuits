# Module:   dispatcher
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Dispatchers

This module implements URL dispatchers.
"""

import os

from circuits import handler, Component

from errors import HTTPError
from cgifs import FieldStorage
from tools import expires, serve_file
from utils import parseQueryString, dictform

class DefaultDispatcher(Component):

    channel = "web"

    def __init__(self, docroot=None, defaults=None, **kwargs):
        super(DefaultDispatcher, self).__init__(**kwargs)

        self.docroot = docroot or os.getcwd()
        self.defaults = defaults or ["index.xhtml", "index.html", "index.htm"]

    def _parseBody(self, request, response, params):
        body = request.body
        headers = request.headers

        if "Content-Type" not in headers:
            headers["Content-Type"] = ""

        try:
            form = FieldStorage(fp=body,
                headers=headers,
                environ={"REQUEST_METHOD": "POST"},
                keep_blank_values=True)
        except Exception, e:
            if e.__class__.__name__ == 'MaxSizeExceeded':
                # Post data is too big
                return HTTPError(request, response, 413)
            else:
                raise

        if form.file:
            request.body = form.file
        else:
            params.update(dictform(form))

        return True

    def _getChannel(self, request):
        """_getChannel(request) -> channel

        Find and return an appropriate channel for the given request.

        The channel is found by traversing the system's event channels,
        and matching path components to successive channels in the system.

        If a channel cannot be found for a given path, but there is
        a default channel, then this will be used.
        """

        path = request.path
        method = request.method.upper()
        request.index = path.endswith("/")

        defaults = "index", method, "default"

        if not "/" in path:
            for default in defaults:
                k = "/:%s" % default
                if k in self.manager.channels:
                    return k, []
            return None, []

        names = [x for x in path.strip("/").split("/") if x]

        targets = set([x.split(":")[0] for x in self.manager.channels if x and \
                ":" in x and x[0] == "/"])

        i = 0
        matches = [""]
        candidates = []
        while i <= len(names):
            x = "/".join(matches) or "/"
            if x in targets:
                candidates.append([i, x])
                if i < len(names):
                    matches.append(names[i])
            else:
                break
            i += 1

        if not candidates:
            return None, []

        i, candidate = candidates.pop()

        if i < len(names):
            channels = [names[i], "index", method, "default"]
        else:
            channels = ["index", method, "default"]

        vpath = []
        channel = None
        for ch in channels:
            x = "%s:%s" % (candidate, ch)
            found = x in self.manager.channels
            if found:
                if i < len(names) and ch == names[i]:
                    i += 1
                channel = x
                break

        if channel is not None:
            if i < len(names):
                vpath = [x.replace("%2F", "/") for x in names[i:]]
            else:
                vpath = []

        return channel, vpath

    @handler("request", filter=True)
    def request(self, event, request, response):
        req = event
        path = request.path.strip("/")

        filename = None

        if path:
            filename = os.path.abspath(os.path.join(self.docroot, path))
        else:
            for default in self.defaults:
                filename = os.path.abspath(os.path.join(self.docroot, default))
                if os.path.exists(filename):
                    break

        if filename and os.path.exists(filename):
            expires(request, response, 3600*24*30)
            return serve_file(request, response, filename)

        channel, vpath = self._getChannel(request)

        if channel:
            req.kwargs = parseQueryString(request.qs)
            v = self._parseBody(request, response, req.kwargs)
            if not v:
                return v # MaxSizeExceeded (return the HTTPError)

            if vpath:
                req.args += tuple(vpath)

            return self.send(req, channel, errors=True)

class FileDispatcher(Component):

   template = """\
<html>
 <head>
  <title>Index of %(path)s</title>
 </head>
 <body>
  <h1>Index of %(path)s</h1>
%(files)s
 </body>
</html>"""

   def __init__(self, path=None, **kwargs):
      super(FileDispatcher, self).__init__(**kwargs)

      if not path:
         self.path = os.getcwd()

   def request(self, request, response):
      print request
      path = request.path.strip("/")
      print path

      # TODO: Re-implement this...

      return self.template

Dispatcher = DefaultDispatcher
FileServer = FileDispatcher
