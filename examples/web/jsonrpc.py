#!/usr/bin/env python
"""
curl -i http://localhost:8000/ -H 'Content-Type: application/json' \
-d '{"id": "test", "method": "test", "params": {"foo": "bar"}}'
"""

from circuits import Component
from circuits.web import JSONRPC, Logger, Server


class Test(Component):
    def foo(self, a, b, c):
        return a, b, c


app = Server(('0.0.0.0', 8000))
Logger().register(app)
JSONRPC().register(app)
Test().register(app)
app.run()
