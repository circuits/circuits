#!/usr/bin/env python

from circuits.web import Controller

from .helpers import urlencode, urlopen, Request


class Root(Controller):

    def index(self, *args, **kwargs):
        args = tuple((x.encode("utf-8") if type(x) != str else x \
                for x in args))
        return "{0}\n{1}".format(repr(args), repr(kwargs))


def test(webapp):
    from circuits import Debugger
    Debugger().register(webapp)

    args = ("1", "2", "3")
    kwargs = {"data": "\x00" * 4096}
    headers = {"Expect": "100-continue"}
    url = "%s/%s" % (webapp.server.base, "/".join(args))
    data = urlencode(kwargs).encode('utf-8')

    req = Request(url, data, headers)
    res = urlopen(req)

    data = res.read().decode('utf-8').split("\n")
    assert data[0] == repr(args)
    assert data[1] == repr(kwargs)
