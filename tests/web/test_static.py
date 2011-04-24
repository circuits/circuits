from circuits.web import Controller

from .helpers import urlopen, HTTPError


class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == b"Hello World!"

def test_404(webapp):
    try:
        urlopen("%s/foo" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_file(webapp):
    url = "%s/static/helloworld.txt" % webapp.server.base
    f = urlopen(url)
    s = f.read().strip()
    assert s == b"Hello World!"

def test_file404(webapp):
    try:
        urlopen("%s/static/foo.txt" % webapp.server.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False

def test_directory(webapp):
    f = urlopen("%s/static/" % webapp.server.base)
    s = f.read()
    assert b"helloworld.txt" in s
