#!/usr/bin/env python

from circuits.web import Server, Controller
from circuits.web.tools import check_auth, basic_auth

class Root(Controller):

    def index(self):
        realm = "Test"
        users = {"admin": "admin"}
        encrypt = str

        if check_auth(self.request, self.response, realm, users, encrypt):
            return "Hello %s" % self.request.login

        return basic_auth(self.request, self.response, realm, users, encrypt)

(Server(8000) + Root()).run()
