#!/usr/bin/env python

from os import path


from circuits.web import Controller


from .conftest import DOCROOT
from .helpers import quote, urlopen, HTTPError


class Root(Controller):

    def index(self):
        return "Hello World!"


def test(webapp):
    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"


def test_404(webapp):
    try:
        urlopen("%s/foo" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False


def test_file(webapp):
    url = "%s/static/helloworld.txt" % webapp.server.http.base
    f = urlopen(url)
    s = f.read().strip()
    assert s == b"Hello World!"


def test_largefile(webapp):
    url = "%s/static/largefile.txt" % webapp.server.http.base
    f = urlopen(url)
    s = f.read().strip()
    assert s == open(path.join(DOCROOT, "largefile.txt"), "r").read()


def test_file404(webapp):
    try:
        urlopen("%s/static/foo.txt" % webapp.server.http.base)
    except HTTPError as e:
        assert e.code == 404
        assert e.msg == "Not Found"
    else:
        assert False


def test_directory(webapp):
    f = urlopen("%s/static/" % webapp.server.http.base)
    s = f.read()
    assert b"helloworld.txt" in s


def test_file_quoating(webapp):
    url = "{0:s}{1:s}".format(webapp.server.http.base, quote("/static/#foobar.txt"))
    f = urlopen(url)
    s = f.read().strip()
    assert s == b"Hello World!"
