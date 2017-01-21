"""JSON RPC

This module implements a JSON RPC dispatcher that translates incoming
RPC calls over JSON into RPC events.
"""
from circuits import BaseComponent, Event, handler
from circuits.six import binary_type
from circuits.tools import tryimport

json = tryimport(("json", "simplejson"))


class rpc(Event):

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

    @handler("request", priority=0.2)
    def _on_request(self, event, req, res):
        if self.path is not None and self.path != req.path.rstrip("/"):
            return

        res.headers["Content-Type"] = "application/json"

        try:
            data = req.body.read().decode(self.encoding)
            o = json.loads(data)
            id, method, params = o["id"], o["method"], o.get("params", {})
            if isinstance(params, dict):
                params = dict([(str(k), v) for k, v in params.iteritems()])

            method = str(method) if not isinstance(method, binary_type) else method

            if isinstance(params, dict):
                value = yield self.call(rpc.create(method, **params), self.rpc_channel)
            else:
                value = yield self.call(rpc.create(method, *params), self.rpc_channel)

            yield self._response(id, value.value)
        except Exception as e:
            yield self._error(-1, 100, "%s: %s" % (e.__class__.__name__, e))
        finally:
            event.stop()

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
