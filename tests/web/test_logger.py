#!/usr/bin/env python
import re
import sys
from socket import gaierror, gethostbyname, gethostname

from circuits.web import Controller, Logger

from .helpers import urlopen

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # NOQA


class DummyLogger(object):

    def __init__(self):
        super(DummyLogger, self).__init__()

        self.message = None

    def info(self, message):
        self.message = message


class Root(Controller):

    def index(self):
        return "Hello World!"


def test_file(webapp):
    logfile = StringIO()
    logger = Logger(file=logfile)
    logger.register(webapp)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    logfile.seek(0)
    s = logfile.read().strip()

    try:
        address = gethostbyname(gethostname())
    except gaierror:
        address = "127.0.0.1"

    d = {}
    d["h"] = address
    d["l"] = "-"
    d["u"] = "-"
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    keys = list(d.keys())

    for k in keys:
        if d[k] and d[k].startswith("127."):
            # loopback network: 127.0.0.0/8
            assert re.search(r"127(\.[0-9]{1,3}){3}", s)
        else:
            assert d[k] in s

    logfile.close()
    logger.unregister()


def test_logger(webapp):
    logobj = DummyLogger()
    logger = Logger(logger=logobj)
    logger.register(webapp)

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    s = logobj.message

    try:
        address = gethostbyname(gethostname())
    except gaierror:
        address = "127.0.0.1"

    d = {}
    d["h"] = address
    d["l"] = "-"
    d["u"] = "-"
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    keys = list(d.keys())

    for k in keys:
        if d[k] and d[k].startswith("127."):
            # loopback network: 127.0.0.0/8
            assert re.search(r"127(\.[0-9]{1,3}){3}", s)
        else:
            assert d[k] in s

    logger.unregister()


def test_filename(webapp, tmpdir):
    logfile = str(tmpdir.ensure("logfile"))
    logger = Logger(file=logfile)
    logger.register(webapp)

    logfile = open(logfile, "r")

    f = urlopen(webapp.server.http.base)
    s = f.read()
    assert s == b"Hello World!"

    logfile.seek(0)
    s = logfile.read().strip()

    try:
        address = gethostbyname(gethostname())
    except gaierror:
        address = "127.0.0.1"

    d = {}
    d["h"] = address
    d["l"] = "-"
    d["u"] = "-"
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    keys = list(d.keys())

    for k in keys:
        if d[k] and d[k].startswith("127."):
            # loopback network: 127.0.0.0/8
            assert re.search(r"127(\.[0-9]{1,3}){3}", s)
        else:
            assert d[k] in s

    logfile.close()
    logger.unregister()
