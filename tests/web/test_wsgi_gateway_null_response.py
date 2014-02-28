#!/usr/bin/env python

from .helpers import urlopen

from circuits.web import Controller


class Root(Controller):

    def index(self, *args, **kwargs):
        return "ERROR"


def application(environ, start_response):
    status = "200 OK"
    start_response(status, [])
    return [""]


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b""
