from circuits.web import Controller

from .helpers import HTTPError, urlopen


class Root(Controller):
    def index(self) -> None:
        pass


def test(webapp) -> None:
    try:
        urlopen(webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == 'Not Found'
    else:
        raise AssertionError
