#!/usr/bin/env python

"""Echo Service

A simple service implementing an Ech Server
"""

from optparse import OptionParser

from circuits import handler
from circuits.net.sockets import TCPServer, Write

from service import install_service, remove_service, Service

__version__ = "0.0.1"

USAGE = "%prog [<options>] install|remove"
VERSION = "%prog v" + __version__

class EchoServer(TCPServer):

    def read(self, sock, data):
        self.push(Write(sock, data))
    
class EchoService(Service):

    @handler("started")
    def _on_started(self, component, mode):
        EchoServer(8000).register(self)

def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    #parser.add_option("-x", "--xxx",
    #       action="store", type="string",
    #       default=None, dest="x",
    #       help="xxx")

    opts, args = parser.parse_args()

    if (args and args[0] not in ("install", "remove",)) or not args:
        parser.print_usage()
        raise SystemExit, -1

    return opts, args

def main():
    opts, args = parse_options()

    if args[0] == "install":
        install_service(EchoServer, "echo_service")
    elif args[0] == "remove":
        remove_service("echo_service")

if __name__ == "__main__":
    main()
