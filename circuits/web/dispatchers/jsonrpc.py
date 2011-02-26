# Module:   jsonrpc
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""JSON RPC

This module implements a JSON RPC dispatcher that translates incoming
RPC calls over JSON into RPC events.
"""

from circuits.tools import tryimport

json = tryimport(("json", "simplejson",))

from circuits.web.events import Response
from circuits import handler, Event, BaseComponent


class RPC(Event):
    """RPC Event"""


class JSONRPC(BaseComponent):

    channel = "web"

    def __init__(self, path=None, target="*", encoding="utf-8"):
        super(JSONRPC, self).__init__()

        if json is None:
            raise RuntimeError("No json support available")

        self.path = path
        self.target = target
        self.encoding = encoding

    @handler("value_changed")
    def _on_value_changed(self, value):
        id = value.id
        response = value.response
        response.body = self._response(id, value.value)
        self.push(Response(response), target=self.channel)

    @handler("request", filter=True, priority=0.1)
    def _on_request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "application/javascript"

        try:
            data = request.body.read()
            o = json.loads(data)
            id, method, params = o["id"], o["method"], o["params"]
            if type(params) is dict:
                params = dict([(str(k), v) for k, v in params.iteritems()])

            if "." in method:
                t, c = method.split(".", 1)
            else:
                t, c = self.target, method

            if type(params) is dict:
                value = self.push(RPC(**params), c, t)
            else:
                value = self.push(RPC(*params), c, t)

            value.id = id
            value.response = response
            value.onSet = ("value_changed", self)
        except Exception, e:
            r = self._error(-1, 100, "%s: %s" % (e.__class__.__name__, e))
            return r
        else:
            return True

    def _response(self, id, result):
        data = {
                "id": id,
                "version": "1.1",
                "result": result,
                "error": None
                }
        return json.dumps(data, encoding=self.encoding)

    def _error(self, id, code, message):
        data = {
                "id": id,
                "version": "1.1",
                "error": {
                    "name": "JSONRPCError",
                    "code": code,
                    "message": message
                    }
                }
        return json.dumps(data, encoding=self.encoding)
