# Module:   dispatcher
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Dispatcher

This module implements a basic URL to Channel dispatcher.
This is the default dispatcher used by circuits.web
"""

from cgi import FieldStorage

from circuits import handler, BaseComponent

from circuits.web.errors import HTTPError
from circuits.web.controllers import BaseController
from circuits.web.utils import parseQueryString, dictform


class Dispatcher(BaseComponent):

    channel = "web"

    def __init__(self, **kwargs):
        super(Dispatcher, self).__init__(**kwargs)

        self.paths = set(["/"])

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
        request.index = request.path.endswith("/")

        names = [x for x in path.strip("/").split("/") if x]

        if not names:
            for default in ("index", method, "default"):
                k = ("/", default)
                if k in self.channels:
                    return default, "/", []
            return None, None, []

        i = 0
        matches = [""]
        candidates = []
        while i <= len(names):
            x = "/".join(matches) or "/"
            if x in self.paths:
                candidates.append([i, x])
                if i < len(names):
                    matches.append(names[i])
            else:
                break
            i += 1

        if not candidates:
            return None, None, []

        vpath = []
        channel = None
        for i, candidate in reversed(candidates):
            if i < len(names):
                channels = [names[i], "index", method, "default"]
            else:
                channels = ["index", method, "default"]

            found = False
            for channel in channels:
                if (candidate, channel) in self.channels:
                    if i < len(names) and channel == names[i]:
                        i += 1
                    found = True
                    break

            if found:
                if channel == "index" and not request.index:
                    continue
                else:
                    break

        if channel is not None:
            if i < len(names):
                vpath = [x.replace("%2F", "/") for x in names[i:]]
            else:
                vpath = []

        if not (candidate, channel) in self.channels:
            return None, None, []
        else:
            handler = self.channels[(candidate, channel)][0]
            if vpath and not (handler.args
                    or handler.varargs
                    or handler.varkw):
                return None, None, []
            else:
                return channel, candidate, vpath

    @handler("registered", target="*")
    def _on_registered(self, c, m):
        if isinstance(c, BaseController) and c not in self.components:
            self.paths.add(c.channel)
            c.unregister()
            self += c

    @handler("unregistered", target="*")
    def _on_unregistered(self, c, m):
        if (isinstance(c, BaseController)
                and c in self.components
                and m == self):
            self.paths.remove(c.channel)

    @handler("request", filter=True, priority=0.1)
    def _on_request(self, event, request, response, peer_cert=None):
        req = event
        if peer_cert:
            req.peer_cert = peer_cert

        channel, target, vpath = self._getChannel(request)

        if channel and target:
            req.kwargs = parseQueryString(request.qs)
            v = self._parseBody(request, response, req.kwargs)
            if not v:
                return v  # MaxSizeExceeded (return the HTTPError)

            if vpath:
                req.args += tuple(vpath)

            return self.push(req, channel, target)
