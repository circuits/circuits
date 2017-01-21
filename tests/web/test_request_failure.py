#!/usr/bin/env python
from circuits.core.components import BaseComponent
from circuits.core.handlers import handler

from .helpers import HTTPError, urlopen


class Root(BaseComponent):

    channel = "web"

    @handler("request", priority=0.2)
    def request(self, request, response):
        raise Exception()


def test(webapp):
    try:
        Root().register(webapp)
        urlopen(webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 500
    else:
        assert False
