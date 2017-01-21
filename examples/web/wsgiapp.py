#!/usr/bin/env python
from circuits.web import Controller
from circuits.web.wsgi import Application


class Root(Controller):

    def index(self):
        return "Hello World!"


application = Application()
Root().register(application)
