#!/usr/bin/env python
from circuits.web import Controller

from .helpers import HTTPError, urlopen

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_root(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"


def test_badpath_notfound(webapp):
    try:
        url = "%s/../../../../../../etc/passwd" % webapp.server.http.base
        urlopen(url)
    except HTTPError as e:
        assert e.code == 404
    else:
        assert False


def test_badpath_redirect(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    path = "/../../../../../../etc/passwd"

    connection.request("GET", path)
    response = connection.getresponse()
    assert response.status == 301
    assert response.reason == "Moved Permanently"

    connection.close()
