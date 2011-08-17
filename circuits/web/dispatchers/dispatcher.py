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

from circuits.web.errors import HTTPError, NotFound
from circuits.web.events import Request, Response
from circuits.web.controllers import BaseController
from circuits.web.tools import expires, serve_file
from circuits.web.utils import parseQueryString, dictform
from ..events import RequestSuccess

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

        parts = [x for x in path.strip("/").split("/") if x]

        if not parts:
            component = self.paths.get("/", None)
            if component is not None:
                for default in ("index", method, "default"):
                    if default in component._handlers:
                        return default, component, []
            return None, None, []

        i = 0
        matches = [""]
        candidates = []
        while i <= len(parts):
            x = "/".join(matches) or "/"
            if x in self.paths:
                candidates.append([i, x])
                if i < len(parts):
                    matches.append(parts[i])
            else:
                break
            i += 1

        if not candidates:
            return None, None, []

        vpath = []
        name = None
        for i, candidate in reversed(candidates):
            if i < len(parts):
                names = [parts[i], "index", method, "default"]
            else:
                names = ["index", method, "default"]

            found = False
            for name in names:
                if name in self.paths[candidate]._handlers:
                    if i < len(names) and name == names[i]:
                        i += 1
                    found = True
                    break

            if found:
                if name == "index" and not request.index:
                    continue
                else:
                    break

        if name is not None:
            if i < len(parts):
                vpath = [x.replace("%2F", "/") for x in parts[i:]]
            else:
                vpath = []

        component = self.paths.get(candidate, None)
        if component is None:
            return None, None, []

        if name not in component._handlers:
            return None, None, []

        handler = list(component._handlers[name])[0]
        if vpath and not (handler.args or handler.varargs or handler.varkw):
            return None, None, []

        return name, candidate, vpath

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

            if isinstance(name, unicode):
                name = str(name)

            e = Request.create(name.title(), *req.args, **req.kwargs)
            return self.fire(e, channel)
        else:
            # this event will have none in the value thus triggering a 404 in request_success
            # this seems convoluted to me
            self.fire(RequestSuccess(event), "web")
