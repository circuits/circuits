#!/usr/bin/env python

from circuits.web import Server
from circuits.web.controllers import BaseController


class Root(BaseController):

    def index(self):
        return "Hello World!"

(Server(8000) + Root()).run()
