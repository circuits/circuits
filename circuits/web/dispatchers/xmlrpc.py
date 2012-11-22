# Module:   xmlrpc
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""XML RPC

This module implements a XML RPC dispatcher that translates incoming
RPC calls over XML into RPC events.
"""

try:
    from xmlrpc.client import dumps, loads, Fault
except ImportError:
    from xmlrpclib import dumps, loads, Fault

from circuits.web.events import Response
from circuits import handler, Event, BaseComponent


class RPC(Event):
    """RPC Event"""


class XMLRPC(BaseComponent):

    channel = "web"

    def __init__(self, path=None, encoding="utf-8", rpc_channel="*"):
        super(XMLRPC, self).__init__()

        self.path = path
        self.encoding = encoding
        self.rpc_channel = rpc_channel

    @handler("request", filter=True, priority=0.2)
    def _on_request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "text/xml"

        try:
            data = request.body.read()
            params, method = loads(data)

            if "." in method:
                channel, name = method.split(".", 1)
            else:
                channel, name = self.rpc_channel, method

            if not isinstance(name, bytes):
                name = name.encode('utf-8')

            @handler("%s_value_changed" % name, priority=0.1)
            def _on_value_changed(self, value):
                response = value.response
                response.body = self._response(value.value)
                self.fire(Response(response), self.channel)
                value.handled = True

            self.addHandler(_on_value_changed)

            value = self.fire(RPC.create(name.title(), *params), channel)
            value.response = response
            value.notify = True
        except Exception as e:
            r = self._error(1, "%s: %s" % (type(e), e))
            return r
        else:
            return True

    def _response(self, result):
        return dumps((result,), encoding=self.encoding,
            allow_none=True)

    def _error(self, code, message):
        fault = Fault(code, message)
        return dumps(fault, encoding=self.encoding, allow_none=True)
