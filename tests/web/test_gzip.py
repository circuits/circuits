#!/usr/bin/env python

try:
    from gzip import decompress
except ImportError:
    import zlib
    decompress = zlib.decompressobj(16+zlib.MAX_WBITS).decompress

try:
    from urllib.request import Request
except ImportError:
    from urllib2 import Request

from circuits import handler, Component

from circuits.web import Controller
from circuits.web.tools import gzip

from .helpers import build_opener


class Gzip(Component):

    channel = "web"

    @handler("response", filter=True)
    def _on_response(self, event, *args, **kwargs):
        event[0] = gzip(event[0])

class Root(Controller):

    def index(self):
        return "Hello World!"

def test(webapp):
    gzip = Gzip()
    gzip.register(webapp)

    request = Request(webapp.server.base)
    request.add_header("Accept-Encoding", "gzip")
    opener = build_opener()

    f = opener.open(request)
    s = decompress(f.read())
    assert s == b"Hello World!"

    gzip.unregister()
