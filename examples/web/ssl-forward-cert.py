#!/usr/bin/env python
# stdlib
import ssl

from circuits.web import Controller, Server


class Root(Controller):

    def GET(self, peer_cert=None):
        return "Here's your cert %s" % peer_cert


app = Server(
    ("0.0.0.0", 8443),
    ssl=True, certfile="server-cert.pem", keyfile="server-key.pem",
    ca_certs="ca-chain.pem", cert_reqs=ssl.CERT_OPTIONAL
)
Root().register(app)
app.run()
