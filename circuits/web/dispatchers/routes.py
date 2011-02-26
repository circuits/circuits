# Module:   routes
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Routes

This module implements a routes based dispatcher.
"""

from circuits.tools import tryimport

routes = tryimport(("routes",))

from circuits import handler, BaseComponent

from cgi import FieldStorage
from circuits.web.errors import HTTPError
from circuits.web.utils import parseQueryString, dictform


class RoutesError(Exception):
    pass


class Routes(BaseComponent):
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

        super(Routes, self).__init__(**kwargs)

        if routes is None:
            raise RuntimeError("No routes support available")

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
                    raise RoutesError("Controller %s must be " + \
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

        path = request.path
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
    def _on_request(self, event, request, response):
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
                return v  # MaxSizeExceeded (return the HTTPError)

            if vpath:
                req.args += tuple(vpath)

            return self.push(req, channel, target=target)

    @handler("registered", target="*")
    def _on_registered(self, event, component, manager):
        """
        Listen for controllers being added to the system and add them
        to the controller index.
        """

        if component.channel and component.channel.startswith("/"):
            self.controllers[component.channel.strip("/")] = component.channel

    @handler("unregistered", target="*")
    def _on_unregistered(self, event, component, manager):
        """
        Listen for controllers being removed from the system and remove them
        from the controller index.
        """

        if component.channel and component.channel.startswith("/"):
            self.controllers.pop(component.channel.strip("/"), None)
