#!/usr/bin/env python

import sys
from urllib2 import urlopen
from StringIO import StringIO

from circuits.web import Controller, Logger
from circuits.web.loggers import formattime

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

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    logfile.seek(0)
    s = logfile.read().strip()

    format = logger.format

    d = {}
    d["h"] = "127.0.0.1"
    d["l"] = "-"
    d["u"] = "-"
    d["t"] = formattime()
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    keys = d.keys()
    keys.remove("t")

    for k in keys:
        assert d[k] in s

    logfile.close()
    logger.unregister()

def test_logger(webapp):
    logobj = DummyLogger()
    logger = Logger(logger=logobj)
    logger.register(webapp)

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    s = logobj.message

    format = logger.format

    d = {}
    d["h"] = "127.0.0.1"
    d["l"] = "-"
    d["u"] = "-"
    d["t"] = formattime()
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    m = format % d
    assert s == m

    logger.unregister()

def test_filename(webapp, tmpdir):
    logfile = str(tmpdir.ensure("logfile"))
    logger = Logger(file=logfile)
    logger.register(webapp)

    logfile = open(logfile, "r")

    f = urlopen(webapp.server.base)
    s = f.read()
    assert s == "Hello World!"

    logfile.seek(0)
    s = logfile.read().strip()

    format = logger.format

    d = {}
    d["h"] = "127.0.0.1"
    d["l"] = "-"
    d["u"] = "-"
    d["t"] = formattime()
    d["r"] = "GET / HTTP/1.1"
    d["s"] = "200"
    d["b"] = "12"
    d["f"] = ""
    d["a"] = "Python-urllib/%s" % sys.version[:3]

    keys = d.keys()
    keys.remove("t")

    for k in keys:
        assert d[k] in s

    logfile.close()
    logger.unregister()
