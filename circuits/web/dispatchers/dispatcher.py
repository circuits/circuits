# Module:   dispatcher
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Dispatcher

This module implements a basic URL to Channel dispatcher.
This is the default dispatcher used by circuits.web
"""

try:
    unicodestr = unicode
except NameError:
    unicodestr = str

from circuits import handler, BaseComponent

from circuits.web.events import Request
from circuits.web.controllers import BaseController
from circuits.web.utils import parse_body, parse_qs


class Dispatcher(BaseComponent):

    channel = "web"

    def __init__(self, **kwargs):
        super(Dispatcher, self).__init__(**kwargs)

        self.paths = dict()

    def resolve_path(self, paths, parts):

        def rebuild_path(url_parts):
            return '/%s' % '/'.join(url_parts)

        left_over = []

        while parts:
            if rebuild_path(parts) in self.paths:
                yield rebuild_path(parts), left_over
            left_over.insert(0, parts.pop())

        if '/' in self.paths:
            yield '/', left_over

    def resolve_methods(self, parts):
        if parts:
            method = parts[0]
            vpath = parts[1:]
            yield method, vpath

        yield 'index', parts

    def find_handler(self, request):
        def get_handlers(path, method):
            component = self.paths[path]
            return component._handlers.get(method, None)

        def accepts_vpath(handlers, vpath):
            args_no = len(vpath)
            return all(len(h.args) == args_no or h.varargs for h in handlers)

        # Split /hello/world to ['hello', 'world']
        starting_parts = [x for x in request.path.strip("/").split("/") if x]

        for path, parts in self.resolve_path(self.paths, starting_parts):
            for method, vpath in self.resolve_methods(parts):
                handlers = get_handlers(path, method)
                if handlers and (not vpath or accepts_vpath(handlers, vpath)):
                    request.index = (method == 'index')
                    return method, path, vpath

        return None, None, None

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
        if peer_cert:
            event.peer_cert = peer_cert

        name, channel, vpath = self.find_handler(request)

        if name is not None and channel is not None:
            event.kwargs = parse_qs(request.qs)
            parse_body(request, response, event.kwargs)

            if vpath:
                event.args += tuple(vpath)

            if isinstance(name, unicodestr):
                name = str(name)

            return self.fire(Request.create(name,
                *event.args, **event.kwargs), channel)
