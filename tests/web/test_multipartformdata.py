#!/usr/bin/env python

from StringIO import StringIO
from urllib2 import urlopen, Request

from circuits.web import Controller

from multipartform import MultiPartForm

class Root(Controller):

    def index(self, file, description=""):
        yield "Filename: %s\n" % file.filename
        yield "Description: %s\n" % description
        yield "Content:\n"
        yield file.value

def test(webapp):
    form = MultiPartForm()
    form["description"] = "Hello World!"

    fd = StringIO("Hello World!")
    form.add_file("file", "helloworld.txt", fd)

    # Build the request
    request = Request(webapp.server.base)
    body = str(form)
    request.add_header("Content-Type", form.get_content_type())
    request.add_header("Content-Length", len(body))
    request.add_data(body)

    f = urlopen(request)
    s = f.read()
    lines = s.split("\n")

    assert lines[0] == "Filename: helloworld.txt"
    assert lines[1] == "Description: Hello World!"
    assert lines[2] == "Content:"
    assert lines[3] == "Hello World!"
