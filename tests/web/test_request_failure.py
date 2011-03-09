from urllib.request import urlopen
from urllib.error import HTTPError

from circuits import Component

class Root(Component):

    channel = "web"

    def request(self, request, response):
        raise Exception()

def test(webapp):
    try:
        f = urlopen(webapp.server.base)
    except HTTPError as e:
        assert e.code == 500
    else:
        assert False
