from circuits.web import Controller

from .helpers import urlencode, urlopen, HTTPError

class Root(Controller):

    def index(self):
        return "Hello World!".encode('utf-16be')

    def foo(self):
        return b"Hello World!".decode()


def test_utf_16_manual(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!".encode('utf-16be')


def test_utf_16_server():
    from circuits import Component

    class WebApp(Component):
        def __init__(self):
            super(WebApp, self).__init__()
            from circuits.web import Server
            self.server = Server(0, encoding='utf-16be').register(self)

    webapp = WebApp()
    Root().register(webapp)

    webapp.start()

    try:
        f = urlopen("%s/foo" % webapp.server.base)
        s = f.read()
        assert s == "Hello World!".encode('utf-16be')
    finally:
        webapp.stop()
