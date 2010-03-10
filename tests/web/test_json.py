#!/usr/bin/env python

import urllib2
from urllib2 import urlopen
from cookielib import CookieJar

try:
    import json
    HAS_JSON = 2
except ImportError:
    try:
        import simplejson as json
        HAS_JSON = 1
    except ImportError:
        HAS_JSON = 0

if HAS_JSON:
    from circuits.web import JSONController, Sessions

    class Root(JSONController):

        def index(self):
            return {"success": True, "message": "Hello World!"}

        def test_sessions(self, name=None):
            if name:
                self.session["name"] = name
            else:
                name = self.session.get("name", "World!")

            return {"success": True, "message": "Hello %s" % name}

    def test(webapp):
        f = urlopen(webapp.server.base)
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello World!"

    def test_sessions(webapp):
        Sessions().register(webapp)

        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        f = opener.open("%s/test_sessions" % webapp.server.base)
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello World!"

        f = opener.open("%s/test_sessions/test" % webapp.server.base)
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello test"

        f = opener.open("%s/test_sessions" % webapp.server.base)
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello test"
