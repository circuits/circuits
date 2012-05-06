# Module:   jsonrpc
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""JSON RPC

This module implements a JSON RPC dispatcher that translates incoming
RPC calls over JSON into RPC events.
"""

from circuits.tools import tryimport

json = tryimport(("json", "simplejson"))

from circuits.web.events import Response
from circuits import handler, Event, BaseComponent


class RPC(Event):
    """RPC Event"""


class JSONRPC(BaseComponent):

    channel = "web"

    def __init__(self, path=None, encoding="utf-8", rpc_channel="*"):
        super(JSONRPC, self).__init__()

        if json is None:
            raise RuntimeError("No json support available")

        self.path = path
        self.encoding = encoding
        self.rpc_channel = rpc_channel

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "application/javascript"

        try:
            data = request.body.read().decode(self.encoding)
            o = json.loads(data)
            id, method, params = o["id"], o["method"], o["params"]
            if type(params) is dict:
                params = dict([(str(k), v) for k, v in params.iteritems()])

            if "." in method:
                channel, name = method.split(".", 1)
            else:
                channel, name = self.rpc_channel, method

            if not isinstance(name, bytes):
                name = name.encode('utf-8')

            @handler("%s_value_changed" % name, priority=0.1)
            def _on_value_changed(self, value):
                id = value.id
                response = value.response
                response.body = self._response(id, value.value)
                self.fire(Response(response), self.channel)
                value.handled = True

            self.addHandler(_on_value_changed)

            if type(params) is dict:
                value = self.fire(RPC.create(name, **params), channel)
            else:
                value = self.fire(RPC.create(name, *params), channel)

            value.id = id
            value.response = response
            value.notify = True
        except Exception as e:
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
        return json.dumps(data).encode(self.encoding)

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
        return json.dumps(data).encode(self.encoding)
