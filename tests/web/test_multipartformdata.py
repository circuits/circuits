#!/usr/bin/env python

from io import StringIO

try:
    from urllib.request import Request
except ImportError:
    from urllib2 import Request

from circuits.web import Controller

from .multipartform import MultiPartForm
from .helpers import urlopen


class Root(Controller):

    def index(self, file, description=""):
        yield "Filename: %s\n" % file.filename
        yield "Description: %s\n" % description
        yield "Content:\n"
        yield file.value

def test(webapp):
    form = MultiPartForm()
    form["description"] = "Hello World!"

    fd = StringIO(b"Hello World!".decode("utf-8"))
    form.add_file("file", "helloworld.txt", fd)

    # Build the request
    request = Request(webapp.server.base)
    body = str(form).encode('utf-8')
    request.add_header("Content-Type", form.get_content_type())
    request.add_header("Content-Length", len(body))
    request.add_data(body)

    f = urlopen(request)
    s = f.read()
    lines = s.split(b"\n")

    assert lines[0] == b"Filename: helloworld.txt"
    assert lines[1] == b"Description: Hello World!"
    assert lines[2] == b"Content:"
    assert lines[3] == b"Hello World!"
