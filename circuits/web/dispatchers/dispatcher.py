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

from circuits.web.events import Response
from circuits.web.errors import HTTPError
from circuits.web.controllers import BaseController
from circuits.web.tools import expires, serve_file
from circuits.web.utils import parseQueryString, dictform

class Dispatcher(BaseComponent):

    channel = "web"

    def __init__(self, **kwargs):
        super(Dispatcher, self).__init__(**kwargs)

        self.paths = dict()

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
        except Exception as e:
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

    def _get_request_handler(self, request):
        path = request.path

        method = request.method.upper()
        request.index = request.path.endswith("/")

        names = [x for x in path.strip("/").split("/") if x]

        if not names:
            component = self.paths.get("/", None)
            if component is not None:
                for default in ("index", method, "default"):
                    if default in component._handlers:
                        return default, component, []
            return None, None, []

        return None, None, []

        # XXX: Fix me  ...

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

    @handler("registered", channel="*")
    def _on_registered(self, component, manager):
        if (isinstance(component, BaseController) and component.channel not
                in self.paths):
            self.paths[component.channel] = component

    @handler("unregistered", channel="*")
    def _on_unregistered(self, component, manager):
        if (isinstance(component, BaseController) and component.channel in
                self.paths):
            del self.paths[component.channel]

    @handler("request", filter=True, priority=0.1)
    def _on_request(self, event, request, response, peer_cert=None):
        req = event
        if peer_cert:
            req.peer_cert = peer_cert

        name, channel, vpath = self._get_request_handler(request)

        if name is not None and channel is not None:
            req.kwargs = parseQueryString(request.qs)
            v = self._parseBody(request, response, req.kwargs)
            if not v:
                # MaxSizeExceeded (return the HTTPError)
                return v

            if vpath:
                req.args += tuple(vpath)

            return self.fire(req.create(name.title(),
                *req.args, **req.kwargs), channel)
