#!/usr/bin/env python
from io import BytesIO
from os import path

from pytest import fixture

from circuits import Component, handler
from circuits.web import Controller
from circuits.web.tools import gzip

from .conftest import DOCROOT
from .helpers import Request, build_opener


class Gzip(Component):

    channel = "web"

    @handler("response", priority=1.0)
    def _on_response(self, event, *args, **kwargs):
        event[0] = gzip(event[0])


class Root(Controller):

    def index(self):
        return "Hello World!"


@fixture
def gziptool(request, webapp):
    gziptool = Gzip().register(webapp)

    def finalizer():
        gziptool.unregister()

    request.addfinalizer(finalizer)

    return gziptool


def decompress(body):
    import gzip

    zbuf = BytesIO()
    zbuf.write(body)
    zbuf.seek(0)
    zfile = gzip.GzipFile(mode='rb', fileobj=zbuf)
    data = zfile.read()
    zfile.close()
    return data


def test1(webapp, gziptool):
    request = Request(webapp.server.http.base)
    request.add_header("Accept-Encoding", "gzip")
    opener = build_opener()

    f = opener.open(request)
    s = decompress(f.read())
    assert s == b"Hello World!"


def test2(webapp, gziptool):
    request = Request("%s/static/largefile.txt" % webapp.server.http.base)
    request.add_header("Accept-Encoding", "gzip")
    opener = build_opener()

    f = opener.open(request)
    s = decompress(f.read())
    assert s == open(path.join(DOCROOT, "largefile.txt"), "rb").read()
