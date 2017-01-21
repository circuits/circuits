#!/usr/bin/env python
from os import path

from circuits.web import Controller

from .conftest import DOCROOT
from .helpers import HTTPError, quote, urlopen

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection  # NOQA


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
    assert s == open(path.join(DOCROOT, "largefile.txt"), "rb").read()


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


def test_file_quooting(webapp):
    url = "{0:s}{1:s}".format(
        webapp.server.http.base, quote("/static/#foobar.txt"))
    f = urlopen(url)
    s = f.read().strip()
    assert s == b"Hello World!"


def test_range(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)

    connection.request("GET", "%s/static/largefile.txt" %
                       webapp.server.http.base, headers={"Range": "bytes=0-100"})
    response = connection.getresponse()
    assert response.status == 206
    s = response.read()
    assert s == open(path.join(DOCROOT, "largefile.txt"), "rb").read(101)


def test_ranges(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)

    connection.request("GET", "%s/static/largefile.txt" %
                       webapp.server.http.base, headers={"Range": "bytes=0-50,51-100"})
    response = connection.getresponse()
    assert response.status == 206

    # XXX Complete this test.
    # ``response.read()`` is a multipart/bytes-range
    # See: Issue #59
    # s = response.read()
    # assert s == open(path.join(DOCROOT, "largefile.txt"), "rb").read(101)


def test_unsatisfiable_range1(webapp):
    connection = HTTPConnection(webapp.server.host, webapp.server.port)

    connection.request("GET", "%s/static/largefile.txt" %
                       webapp.server.http.base, headers={"Range": "bytes=0-100,100-10000,0-1"})
    response = connection.getresponse()
    assert response.status == 416


# TODO: Implement this test and condition
# e.g: For a 10 byte file; Range: bytes=0-1,2-3,4-5,6-7,8-9
# def test_unsatisfiable_range2(webapp):
#    connection = HTTPConnection(webapp.server.host, webapp.server.port)
#
#    connection.request("GET", "%s/static/largefile.txt" % (webapp.server.http.base,
#       headers={"Range": "bytes=0-100,100-10000,0-1"}))
#    response = connection.getresponse()
#    assert response.status == 416
