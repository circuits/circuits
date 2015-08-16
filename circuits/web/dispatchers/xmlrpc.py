"""XML RPC

This module implements a XML RPC dispatcher that translates incoming
RPC calls over XML into RPC events.
"""

try:
    from xmlrpc.client import dumps, loads, Fault
except ImportError:
    from xmlrpclib import dumps, loads, Fault  # NOQA

from circuits.six import binary_type
from circuits import handler, Event, BaseComponent


class rpc(Event):

    """rpc Event"""


class XMLRPC(BaseComponent):

    channel = "web"

    def __init__(self, path=None, encoding="utf-8", rpc_channel="*"):
        super(XMLRPC, self).__init__()

        self.path = path
        self.encoding = encoding
        self.rpc_channel = rpc_channel

    @handler("request", priority=0.2)
    def _on_request(self, event, req, res):
        if self.path is not None and self.path != req.path.rstrip("/"):
            return

        res.headers["Content-Type"] = "text/xml"

        try:
            data = req.body.read()
            params, method = loads(data)

            method = str(method) if not isinstance(method, binary_type) else method

            value = yield self.call(rpc.create(method, *params), self.rpc_channel)
            yield self._response(value.value)
        except Exception as e:
            yield self._error(1, "%s: %s" % (type(e), e))
        finally:
            event.stop()

    def _response(self, result):
        return dumps((result,), encoding=self.encoding, allow_none=True)

    def _error(self, code, message):
        fault = Fault(code, message)
        return dumps(fault, encoding=self.encoding, allow_none=True)
