from circuits.web import Controller
from circuits.web.tools import basic_auth, check_auth

from .helpers import (
    HTTPBasicAuthHandler, HTTPError, build_opener, install_opener, urlopen,
)


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
        f = urlopen(webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 401
        assert e.msg == "Unauthorized"
    else:
        assert False

    handler = HTTPBasicAuthHandler()
    handler.add_password("Test", webapp.server.http.base, "admin", "admin")
    opener = build_opener(handler)
    install_opener(opener)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"
    install_opener(None)
