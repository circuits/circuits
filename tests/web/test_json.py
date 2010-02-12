#!/usr/bin/env python

from urllib2 import urlopen

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
    from circuits.web import JSONController

    class Root(JSONController):

        def index(self):
            return {"success": True, "message": "Hello World!"}

    def test(webapp):
        f = urlopen(webapp.server.base)
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello World!"
