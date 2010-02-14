#!/usr/bin/env python

from urllib2 import HTTPError, HTTPBasicAuthHandler
from urllib2 import urlopen, build_opener, install_opener

from circuits.web import Controller
from circuits.web.tools import check_auth, basic_auth

class Root(Controller):

    def index(self):
        realm = "Test"
        users = {"admin": "admin"}
        encrypt = str

        if check_auth(self.request, self.response, realm, users, encrypt):
            return "Hello World!"

        return basic_auth(self.request, self.response, realm, users, encrypt)

def test(webapp):
    try:
        f = urlopen(webapp.server.base)
    except HTTPError, e:
        assert e.code == 401
        assert e.msg == "Unauthorized"
    else:
        assert False

    handler = HTTPBasicAuthHandler()
    handler.add_password("Test", webapp.server.base, "admin", "admin")
    opener = build_opener(handler)
    install_opener(opener)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"
