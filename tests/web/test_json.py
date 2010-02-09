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
    from circuits.web import Server, JSONController

    class Root(JSONController):

        def index(self):
            return {"success": True, "message": "Hello World!"}

    app = Server(8000) + Root()

    def test():
        f = urlopen("http://localhost:8000/")
        data = f.read()
        d = json.loads(data)
        assert d["success"]
        assert d["message"] == "Hello World!"

def pytest_session_finish():
    app.stop()
