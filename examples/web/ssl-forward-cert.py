#!/usr/bin/env python

# stdlib
import ssl

from circuits import Event, Component, Debugger
from circuits.net.sockets import TCPClient
from circuits.web import Server, Controller

class Root(Controller):
    def GET(self, peer_cert=None):
        return "Here's your cert %s" % peer_cert

class SSLServer(Server):
    pass

def main():
    ssl_server =  SSLServer(("localhost", 8443), ssl=True, certfile="server-cert.pem", keyfile="server-key.pem",
        ca_certs="ca-chain.pem", cert_reqs=ssl.CERT_OPTIONAL) + Root() + Debugger()
    ssl_server.run()

if __name__ == "__main__":
    main()
