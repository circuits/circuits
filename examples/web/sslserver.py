#!/usr/bin/env python

# stdlib
import ssl

# Circuits
from circuits import Debugger
from circuits.web import Server, Controller

class Root(Controller):

    def index(self):
        return "Hello World!"

(Server(("localhost", 8443), ssl=True, certfile="server-cert.pem", keyfile="server-key.pem",
        ca_certs="ca-chain.pem", cert_reqs=ssl.CERT_NONE) + Debugger() + Root()).run()
