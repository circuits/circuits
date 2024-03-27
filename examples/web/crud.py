#!/usr/bin/env python
from circuits.web import Controller, Logger, Server


class Root(Controller):
    def GET(self, *args, **kwargs):
        """
        GET Request Handler

        The default Dispatcher in circuits.web also looks for GET, POST,
        PUT, DELETE and HEAD Request handlers on registered Controller(s).

        These can be used to implement RESTful resources with CRUD operations.
        """
        return f'GET({args!r:s}, {kwargs!r:s})'

    def POST(self, *args, **kwargs):
        return f'POST({args!r:s}, {kwargs!r:s})'

    def PUT(self, *args, **kwargs):
        return f'PUT({args!r:s}, {kwargs!r:s})'

    def DELETE(self, *args, **kwargs):
        return f'DELETE({args!r:s}, {kwargs!r:s})'

    def HEAD(self, *args, **kwargs):
        return f'HEAD({args!r:s}, {kwargs!r:s})'


app = Server(('0.0.0.0', 8000))
Logger().register(app)
Root().register(app)
app.run()
