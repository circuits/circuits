#!/usr/bin/env python
from circuits.web import Controller, Server
from circuits.web.dispatchers import VirtualHosts


class Root(Controller):

    def index(self):
        return "I am the main vhost"


class Foo(Controller):

    channel = "/foo"

    def index(self):
        return "I am foo."


class Bar(Controller):

    channel = "/bar"

    def index(self):
        return "I am bar."


domains = {
    "foo.localdomain:8000": "foo",
    "bar.localdomain:8000": "bar",
}


app = Server(("0.0.0.0", 8000))
VirtualHosts(domains).register(app)
Root().register(app)
Foo().register(app)
Bar().register(app)
app.run()
