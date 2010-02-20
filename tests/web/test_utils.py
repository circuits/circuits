#!/usr/bin/env python

from StringIO import StringIO

from circuits.web.utils import get_ranges
from circuits.web.utils import compress, decompress
from circuits.web.utils import url_quote, url_unquote

def test_ranges():
    assert get_ranges("bytes=3-6", 8) == [(3, 7)]
    assert get_ranges("bytes=2-4,-1", 8) == [(2, 5), (7, 8)]

def test_gzip():
    body = StringIO("Hello World")
    gziped = "".join(compress(body, 1))
    assert decompress(gziped) == body.getvalue()
    body.close()

def test_quote():
    url = "http://localhost:8000/one page/?q=Hello World"
    assert url_unquote(url_quote(url))
