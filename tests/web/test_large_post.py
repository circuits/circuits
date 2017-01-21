#!/usr/bin/env python
from circuits.web import Controller

from .helpers import urlencode, urlopen


class Root(Controller):

    def index(self, *args, **kwargs):
        args = tuple((
            x.encode("utf-8") if type(x) != str else x
            for x in args
        ))
        return "{0}\n{1}".format(repr(args), repr(kwargs))


def test(webapp):
    args = ("1", "2", "3")
    kwargs = {"data": "\x00" * 4096}
    url = "%s/%s" % (webapp.server.http.base, "/".join(args))
    data = urlencode(kwargs).encode('utf-8')
    f = urlopen(url, data)
    data = f.read().split(b"\n")
    assert eval(data[0]) == args
    assert eval(data[1]) == kwargs
