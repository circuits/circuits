#!/usr/bin/env python


from hashlib import md5


from circuits import handler, Component
from circuits.web import Server, Controller
from circuits.web.tools import check_auth, basic_auth


class Auth(Component):

    realm = "Test"
    users = {"admin": md5("admin").hexdigest()}

    @handler("request", priority=1.0)
    def on_request(self, event, request, response):
        """Filter Requests applying Basic Authentication

        Filter any incoming requests at a higher priority than the
        default dispatcher and apply Basic Authentication returning
        a 403 Forbidden response if Authentication failed.
        """

        if not check_auth(request, response, self.realm, self.users):
            event.stop()
            return basic_auth(request, response, self.realm, self.users)


class Root(Controller):

    def index(self):
        return "Hello World!"

app = Server(("0.0.0.0", 8000))
Auth().register(app)
Root().register(app)
app.run()
