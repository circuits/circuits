# Module:   xmlrpc
# Date:     13th September 2007
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""XML RPC

This module implements a XML RPC dispatcher that translates incoming
RPC calls over XML into RPC events.
"""

import xmlrpclib

from circuits.web.events import Response
from circuits import handler, Event, BaseComponent


class RPC(Event):
    """RPC Event"""


class XMLRPC(BaseComponent):

    channel = "web"

    def __init__(self, path=None, target="*", encoding="utf-8"):
        super(XMLRPC, self).__init__()

        self.path = path
        self.target = target
        self.encoding = encoding

    @handler("value_changed")
    def _on_value_changed(self, value):
        response = value.response
        response.body = self._response(value.value)
        self.push(Response(response), target=self.channel)

    @handler("request", filter=True, priority=0.1)
    def _on_request(self, request, response):
        if self.path is not None and self.path != request.path.rstrip("/"):
            return

        response.headers["Content-Type"] = "text/xml"

        try:
            data = request.body.read()
            params, method = xmlrpclib.loads(data)

            if "." in method:
                t, c = method.split(".", 1)
            else:
                t, c = self.target, method

            value = self.push(RPC(*params), c, t)
            value.response = response
            value.onSet = ("value_changed", self)
        except Exception, e:
            r = self._error(1, "%s: %s" % (type(e), e))
            return r
        else:
            return True

    def _response(self, result):
        return xmlrpclib.dumps((result,), encoding=self.encoding,
            allow_none=True)

    def _error(self, code, message):
        fault = xmlrpclib.Fault(code, message)
        return xmlrpclib.dumps(fault, encoding=self.encoding, allow_none=True)
