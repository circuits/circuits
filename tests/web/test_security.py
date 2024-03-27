#!/usr/bin/env python
from http.client import HTTPConnection

import pytest

from circuits.web import Controller

from .helpers import HTTPError, urlopen


class Root(Controller):
    def index(self):
        return 'Hello World!'


def test_root(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b'Hello World!'


def test_badpath_notfound(webapp):
    url = '%s/../../../../../../etc/passwd' % webapp.server.http.base
    with pytest.raises(HTTPError) as exc:
        urlopen(url)
    assert exc.value.code == 404


def test_badpath_redirect(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)
    connection.connect()

    path = '/../../../../../../etc/passwd'

    connection.request('GET', path)
    response = connection.getresponse()
    assert response.status == 301
    assert response.reason == 'Moved Permanently'

    connection.close()
