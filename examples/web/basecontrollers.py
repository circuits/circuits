#!/usr/bin/env python

from circuits.web import expose, Server
from circuits.web.controllers import BaseController

class Root(BaseController):

    @expose("index")
    def index(self):
        return "Hello World!"

(Server(8000) + Root()).run()
