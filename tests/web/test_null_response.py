from urllib.request import urlopen
from urllib.error import HTTPError

from circuits.web import Controller

class Root(Controller):

    def index(self):
        pass

def test(webapp):
    try:
        urlopen(webapp.server.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False
