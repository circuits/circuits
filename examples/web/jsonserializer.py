#!/usr/bin/env python
from json import dumps

from circuits import Component, handler
from circuits.web import Controller, Logger, Server


class JSONSerializer(Component):

    channel = "web"

    # 1 higher than the default response handler
    @handler("response", priority=1.0)
    def serialize_response_body(self, response):
        response.headers["Content-Type"] = "application/json"
        response.body = dumps(response.body)


class Root(Controller):

    def index(self):
        return {"message": "Hello World!"}


app = Server(("0.0.0.0", 9000))
JSONSerializer().register(app)
Logger().register(app)
Root().register(app)
app.run()
