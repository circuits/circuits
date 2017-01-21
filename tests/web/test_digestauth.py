#!/usr/bin/env python
import pytest

from circuits.web import Controller
from circuits.web.tools import check_auth, digest_auth

from .helpers import (
    HTTPDigestAuthHandler, HTTPError, build_opener, install_opener, urlopen,
)

pytestmark = pytest.mark.skipif(pytest.PYVER[:2] == (3, 3), reason='Broken on Python 3.3')


class Root(Controller):

    def index(self):
        realm = "Test"
        users = {"admin": "admin"}

        if check_auth(self.request, self.response, realm, users):
            return "Hello World!"

        return digest_auth(self.request, self.response, realm, users)


def test(webapp):
    try:
        f = urlopen(webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 401
        assert e.msg == "Unauthorized"
    else:
        assert False

    handler = HTTPDigestAuthHandler()
    handler.add_password("Test", webapp.server.http.base, "admin", "admin")
    opener = build_opener(handler)
    install_opener(opener)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
    install_opener(None)
