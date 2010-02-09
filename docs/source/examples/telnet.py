#!/usr/bin/env python

import os
import optparse
from socket import gethostname
 
from circuits.io import stdin
from circuits import handler, Component
from circuits import __version__ as systemVersion
from circuits.net.sockets import TCPClient, UNIXClient, Connect, Write

USAGE = "%prog [options] host [port]"
VERSION = "%prog v" + systemVersion

def parse_options():
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)
   
    opts, args = parser.parse_args()
   
    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1
   
    return opts, args
   
class Telnet(Component):
   
    channel = "telnet"

    def __init__(self, *args):
        super(Telnet, self).__init__()
   
        if len(args) == 1:
            if os.path.exists(args[0]):
                self += UNIXClient(channel=self.channel)
                host = dest = port = args[0]
                dest = (dest,)
            else:
                raise OSError("Path %s not found" % args[0])
        else:
            self += TCPClient(channel=self.channel)
            host, port = args
            port = int(port)
            dest = host, port
   
        print "Trying %s ..." % host
        self.push(Connect(*dest), "connect")
   
    def connected(self, host, port=None):
        print "Connected to %s" % host
   
    def error(self, *args):
        if len(args) == 3:
            type, value, traceback = args
        else:
            value = args[0]
            type = type(value)
            traceback = None
   
        print "ERROR: %s" % value
   
    def read(self, data):
        print data.strip()
   
    @handler("read", target="stdin")
    def stdin_read(self, data):
        self.push(Write(data), "write")
   
opts, args = parse_options()
(Telnet(*args) + stdin).run()
