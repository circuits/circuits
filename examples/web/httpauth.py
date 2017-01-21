#!/usr/bin/env python
from circuits.web import Controller, Server
from circuits.web.tools import basic_auth, check_auth


class Root(Controller):

    def index(self):
        realm = "Test"
        users = {"admin": "admin"}
        encrypt = str

        if check_auth(self.request, self.response, realm, users, encrypt):
            return "Hello %s" % self.request.login

        return basic_auth(self.request, self.response, realm, users, encrypt)


app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
