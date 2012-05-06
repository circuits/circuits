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
        while parts and rebuild_path(parts) not in self.paths:
            left_over.insert(0, parts.pop())

        return rebuild_path(parts), left_over

    def resolve_method(self, parts):
        if not parts:
            return 'index', ''
        method = parts.pop(0)
        vpath = parts
        return method, vpath

    def find_handler(self, request):
        path = request.path
        method = request.method.upper()
        request.index = request.path.endswith("/")

        # Split /hello/world to ['hello', 'world']
        parts = [x for x in path.strip("/").split("/") if x]

        path, parts = self.resolve_path(self.paths, parts)
        method, vpath = self.resolve_method(parts)

        if not path:
            path = '/'
        if not method:
            method = 'index'
        return method, path, vpath

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
