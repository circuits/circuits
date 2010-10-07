# Module:   dispatcher
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Dispatchers

This module implements URL dispatchers.
"""

import os
import xmlrpclib
from string import Template
from urlparse import urljoin as _urljoin

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

from circuits import handler, Event, Component

from events import Response
from errors import HTTPError
from cgi import FieldStorage
from controllers import BaseController
from tools import expires, serve_file
from utils import parseQueryString, dictform

DEFAULT_DIRECTORY_INDEX_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
        <meta http-equiv="Content-Language" content="en-us" />
        <meta name="robots" content="NONE,NOARCHIVE" />
        <title>Index of $directory</title>
    </head>
    <body>
        <h1>Index of $directory</h1>
        <ul>
            $url_up
            $listing
        </ul>
    </body>
</html>
"""

_dirlisting_template = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE)


class RPC(Event): pass


class Static(Component):

    channel = "web"

    def __init__(self, path=None, docroot=None,
            defaults=("index.html", "index.xhtml",), dirlisting=False):
        super(Static, self).__init__()

        self.path = path
        self.docroot = docroot or os.getcwd()
        self.defaults = defaults
        self.dirlisting = dirlisting

    @handler("request", filter=True, priority=0.9)
    def request(self, request, response):
        if self.path is not None and not request.path.startswith(self.path):
            return

        path = request.path

        if self.path is not None:
            path = path[len(self.path):]
        path = path.strip("/")

        if path:
            location = os.path.abspath(os.path.join(self.docroot, path))
        else:
            location = os.path.abspath(os.path.join(self.docroot, "."))

        if not os.path.exists(location):
            return

        # Is it a file we can serve directly?
        if os.path.isfile(location):
            # Don't set cookies for static content
            response.cookie.clear()
            expires(request, response, 3600*24*30, force=True)
            return serve_file(request, response, location)

        # Is it a directory?
        elif os.path.isdir(location):

            # Try to serve one of default files first..
            for default in self.defaults:
                location = os.path.abspath(
                        os.path.join(self.docroot, path, default))
                if os.path.exists(location):
                    # Don't set cookies for static content
                    response.cookie.clear()
                    expires(request, response, 3600*24*30, force=True)
                    return serve_file(request, response, location)

            # .. serve a directory listing if allowed to.
            if self.dirlisting:
                directory = os.path.abspath(os.path.join(self.docroot, path))
                cur_dir = os.path.join(self.path, path) if self.path else ""

                if not path:
                    url_up = ""
                else:
                    if self.path is None:
                        url_up = os.path.join("/", os.path.split(path)[0])
                    else:
                        url_up = os.path.join(cur_dir, "..")
                    url_up = '<li><a href="%s">%s</a></li>' % (url_up, "..")

                listing = []
                for item in os.listdir(directory):
                    if not item.startswith("."):
                        url = os.path.join("/", path, cur_dir, item)
                        location = os.path.abspath(
                                os.path.join(self.docroot, path, item))
                        if os.path.isdir(location):
                            li = '<li><a href="%s/">%s/</a></li>' % (url, item)
                        else:
                            li = '<li><a href="%s">%s</a></li>' % (url, item)
                        listing.append(li)

                ctx = {}
                ctx["directory"] = cur_dir or os.path.join("/", cur_dir, path)
                ctx["url_up"] = url_up
                ctx["listing"] = "\n".join(listing)
                return _dirlisting_template.safe_substitute(ctx)

class Dispatcher(Component):

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
            if vpath and not (handler.args or handler.varargs or handler.varkw):
                return None, None, []
            else:
                return channel, candidate, vpath

    @handler("registered", target="*")
    def registered(self, c, m):
        if isinstance(c, BaseController) and c not in self.components:
            self.paths.add(c.channel)
            c.unregister()
            self += c

    @handler("unregistered", target="*")
    def unregistered(self, c, m):
        if isinstance(c, BaseController) and c in self.components and m == self:
            self.paths.remove(c.channel)

    @handler("request", filter=True, priority=0.1)
    def request(self, event, request, response, peer_cert=None):
        req = event
        if peer_cert:
            req.peer_cert = peer_cert

        channel, target, vpath = self._getChannel(request)

        if channel and target:
            req.kwargs = parseQueryString(request.qs)
            v = self._parseBody(request, response, req.kwargs)
            if not v:
                return v # MaxSizeExceeded (return the HTTPError)

            if vpath:
                req.args += tuple(vpath)

            return self.push(req, channel, target)

class RoutesDispatcherError(Exception):
    pass

class RoutesDispatcher(Component):
    """A Routes Dispatcher

    A dispatcher that uses the routes module to perform controller
    lookups for a url using pattern matching rules (connections).

    See: http://routes.groovie.org/docs/ for more information on Routes.
    """

    channel = "web"

    def __init__(self, add_default_connection=False, **kwargs):
        """
        If add_default_connection is True then a default connection
        of /{controller}/{action} will be added as part of
        the instantiation. Note that because Routes are order dependant
        this could obscure similar connections added at
        a later date, hence why it is disabled by default.
        """

        super(RoutesDispatcher, self).__init__(**kwargs)

        import routes

        # An index of controllers used by the Routes Mapper when performing
        # matches
        self.controllers = {}
        self.mapper = routes.Mapper(controller_scan=self.controllers.keys)
        if add_default_connection:
            self.connect("default", "/{controller}/{action}")

    def connect(self, name, route, **kwargs):
        """
        Connect a route to a controller

        Supply a name for the route and then the route itself.
        Naming the route allows it to be referred to easily
        elsewhere in the system (e.g. for generating urls).
        The route is the url pattern you wish to map.
        """

        controller = kwargs.pop('controller', None)
        if controller is not None:

            if not isinstance(controller, basestring):
                try:
                    controller = getattr(controller, 'channel')
                except AttributeError:
                    raise RoutesDispatcherError("Controller %s must be " + \
                            "either a string or have a 'channel' property " + \
                            "defined." % controller)

            controller = controller.strip("/")
        self.mapper.connect(name, route, controller=controller, **kwargs)

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
        """Find and return an appropriate channel for the given request.

        The channel is found by consulting the Routes mapper to return a
        matching controller (target) and action (channel) along with a
        dictionary of additional parameters to be added to the request.
        """

        import routes

        path = request.path
        method = request.method.upper()
        request.index = path.endswith("/")

        # setup routes singleton config instance
        config = routes.request_config()
        config.mapper = self.mapper
        config.host = request.headers.get('Host', None)
        config.protocol = request.scheme

        # Redirect handler not supported at present
        config.redirect = None

        result = self.mapper.match(path)
        config.mapper_dict = result
        channel = None
        target = None
        vpath = []
        if result:
            target = self.controllers[result['controller']]
            channel = result["action"]
        return channel, target, vpath, result.copy()

    @handler("request", filter=True)
    def request(self, event, request, response):
        req = event

        # retrieve a channel (handler) for this request
        channel, target, vpath, params = self._getChannel(request)

        if channel:
            # add the params from the routes match
            req.kwargs = params
            # update with any query string params
            req.kwargs.update(parseQueryString(request.qs))
            v = self._parseBody(request, response, req.kwargs)
            if not v:
                return v # MaxSizeExceeded (return the HTTPError)

            if vpath:
                req.args += tuple(vpath)

            return self.push(req, channel, target=target)

    @handler("registered", target="*")
    def registered(self, event, component, manager):
        """
        Listen for controllers being added to the system and add them
        to the controller index.
        """

        if component.channel and component.channel.startswith("/"):
            self.controllers[component.channel.strip("/")] = component.channel

    @handler("unregistered", target="*")
    def unregistered(self, event, component, manager):
        """
        Listen for controllers being removed from the system and remove them
        from the controller index.
        """

        if component.channel and component.channel.startswith("/"):
            self.controllers.pop(component.channel.strip("/"), None)

class VirtualHosts(Component):
    """Forward to anotehr Dispatcher based on the Host header.

    This can be useful when running multiple sites within one server.
    It allows several domains to point to different parts of a single
    website structure. For example:
     - http://www.domain.example      -> /
     - http://www.domain2.example     -> /domain2
     - http://www.domain2.example:443 -> /secure

    :param domains: a dict of {host header value: virtual prefix} pairs.
    :type  domains: dict

    The incoming "Host" request header is looked up in this dict,
    and, if a match is found, the corresponding "virtual prefix"
    value will be prepended to the URL path before passing the
    request onto the next dispatcher.

    Note that you often need separate entries for "example.com"
    and "www.example.com". In addition, "Host" headers may contain
    the port number.
    """

    channel = "web"

    def __init__(self, domains):
        super(VirtualHosts, self).__init__()

        self.domains = domains

    @handler("request", filter=True, priority=1.0)
    def request(self, event, request, response):
        path = request.path.strip("/")

        header = request.headers.get
        domain = header("X-Forwarded-Host", header("Host", ""))
        prefix = self.domains.get(domain, "")

        if prefix:
            path = _urljoin("/%s/" % prefix, path)
            request.path = path

class XMLRPC(Component):

    channel = "web"

    def __init__(self, path=None, target="*", encoding="utf-8"):
        super(XMLRPC, self).__init__()

        self.path = path
        self.target = target
        self.encoding = encoding

    def rpcvalue(self, value):
        response = value.response
        response.body = self._response(value.value)
        self.push(Response(response), target=self.channel)

    @handler("request", filter=True, priority=0.1)
    def request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "text/xml"

        try:
            data = request.body.read()
            params, method = xmlrpclib.loads(data)

            if "." in method:
                t, c = method.split(".", 1)
            else:
                t, c = self.target, method

            value = self.push(RPC(*params), c, t)
            value.response = response
            value.onSet = ("rpcvalue", self)

            #TODO: How do we implement this ?
            #else:
            #    r = self._error(1, "method '%s' does not exist" % method)
        except Exception, e:
            r = self._error(1, "%s: %s" % (type(e), e))
            return r
        else:
            return True

    def _response(self, result):
        return xmlrpclib.dumps((result,), encoding=self.encoding,
            allow_none=True)

    def _error(self, code, message):
        fault = xmlrpclib.Fault(code, message)
        return xmlrpclib.dumps(fault, encoding=self.encoding, allow_none=True)

class JSONRPC(Component):

    channel = "web"

    def __init__(self, path=None, target="*", encoding="utf-8"):
        super(JSONRPC, self).__init__()

        self.path = path
        self.target = target
        self.encoding = encoding

    def rpcvalue(self, value):
        id = value.id
        response = value.response
        response.body = self._response(id, value.value)
        self.push(Response(response), target=self.channel)

    @handler("request", filter=True, priority=0.1)
    def request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "application/javascript"

        try:
            data = request.body.read()
            o = json.loads(data)
            id, method, params = o["id"], o["method"], o["params"]
            if type(params) is dict:
                params = dict([(str(k), v) for k, v in params.iteritems()])

            if "." in method:
                t, c = method.split(".", 1)
            else:
                t, c = self.target, method

            if type(params) is dict:
                value = self.push(RPC(**params), c, t)
            else:
                value = self.push(RPC(*params), c, t)

            value.id = id
            value.response = response
            value.onSet = ("rpcvalue", self)

            #TODO: How do we implement this ?
            #else:
            #    r = self._error(id, 100, "method '%s' does not exist" % method)
        except Exception, e:
            r = self._error(-1, 100, "%s: %s" % (e.__class__.__name__, e))
            return r
        else:
            return True

    def _response(self, id, result):
        data = {
                "id": id,
                "version": "1.1",
                "result": result,
                "error": None
                }
        return json.dumps(data, encoding=self.encoding)

    def _error(self, id, code, message):
        data = {
                "id": id,
                "version": "1.1",
                "error": {
                    "name": "JSONRPCError",
                    "code": code,
                    "message": message
                    }
                }
        return json.dumps(data, encoding=self.encoding)

if not HAS_JSON:
    del JSONRPC
