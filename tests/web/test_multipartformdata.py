#!/usr/bin/env python
from io import BytesIO
from os import path

import pytest

from circuits.web import Controller

from .helpers import Request, urlopen
from .multipartform import MultiPartForm


@pytest.fixture()
def sample_file(request):
    return open(
        path.join(
            path.dirname(__file__),
            "static", "unicode.txt"
        ),
        "rb"
    )


class Root(Controller):

    def index(self, file, description=""):
        yield "Filename: %s\n" % file.filename
        yield "Description: %s\n" % description
        yield "Content:\n"
        yield file.value

    def upload(self, file, description=""):
        return file.value


def test(webapp):
    form = MultiPartForm()
    form["description"] = "Hello World!"

    fd = BytesIO(b"Hello World!")
    form.add_file("file", "helloworld.txt", fd, "text/plain; charset=utf-8")

    # Build the request
    url = webapp.server.http.base
    data = form.bytes()
    headers = {
        "Content-Type": form.get_content_type(),
        "Content-Length": len(data),
    }

    request = Request(url, data, headers)

    f = urlopen(request)
    s = f.read()
    lines = s.split(b"\n")

    assert lines[0] == b"Filename: helloworld.txt"
    assert lines[1] == b"Description: Hello World!"
    assert lines[2] == b"Content:"
    assert lines[3] == b"Hello World!"


def test_unicode(webapp, sample_file):
    form = MultiPartForm()
    form["description"] = sample_file.name
    form.add_file(
        "file", "helloworld.txt", sample_file,
        "text/plain; charset=utf-8"
    )

    # Build the request
    url = "{0:s}/upload".format(webapp.server.http.base)
    data = form.bytes()
    headers = {
        "Content-Type": form.get_content_type(),
        "Content-Length": len(data),
    }

    request = Request(url, data, headers)

    f = urlopen(request)
    s = f.read()
    sample_file.seek(0)
    expected_output = sample_file.read()  # use the byte stream
    assert s == expected_output
