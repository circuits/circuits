#!/usr/bin/env python

import json

from circuits import handler, Component
from circuits.web import Server, Controller, Logger


class JSONSerializer(Component):

    channel = "web"

    @handler("request_filtered", priority=1.0)
    def _on_request_success_or_filtered(self, event, evt, handler, retval):
        request, response = evt.args[:2]

        event[2] = json.dumps(retval.value)
        response.headers["Content-Type"] = "application/json"


class Root(Controller):

    def index(self):
        return {"message": "Hello World!"}

app = Server(("0.0.0.0", 8000))
JSONSerializer().register(app)
Logger().register(app)
Root().register(app)
app.run()
