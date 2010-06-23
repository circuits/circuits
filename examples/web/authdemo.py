#!/usr/bin/env python

from circuits import handler, Component
from circuits.web import Server, Controller
from circuits.web.tools import check_auth, basic_auth

class Auth(Component):

    realm = "Test"
    users = {"admin": "21232f297a57a5a743894a0e4a801fc3"}

    @handler("request", filter=True)
    def on_request(self, request, response):
        realm = self.realm
        users = self.users
        if not check_auth(request, response, realm, users):
            return basic_auth(request, response, realm, users)

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("0.0.0.0", 8000)) + Auth() + Root()).run()
