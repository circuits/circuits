#!/usr/bin/env python

import pytest

from circuits.web import Controller

from circuits.web.client import Client, Connect, Request
from circuits.core.manager import Manager


class Root(Controller):

    def index(self):
        return "Hello World!"


def test(webapp):
    client = Client()
    client.start()

    client.fire(Request("GET", webapp.server.http.base))
    while client.response is None:
        pass

    client.stop()

    response = client.response
    assert response.status == 200
    assert response.message == "OK"

    s = response.read()
    assert s == b"Hello World!"
