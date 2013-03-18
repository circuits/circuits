#!/usr/bin/env python

from circuits.web import Server
from circuits.web.controllers import expose, BaseController


class Root(BaseController):

    @expose("index")
    def index(self):
        """Index Request Handler

        BaseController(s) do not expose methods as request handlers.
        Request Handlers _must_ be exposed explicitly using the ``@expose``
        decorator.
        """

        return "Hello World!"

(Server(9000) + Root()).run()
