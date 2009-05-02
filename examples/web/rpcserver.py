#!/usr/bin/env python

from circuits import Component
from circuits.web import BaseServer, XMLRPC, JSONRPC

class HelloWorld(Component):

    def hello(self):
        return "Hello World!"

(BaseServer(9999) + XMLRPC() + HelloWorld()).run()
#(BaseServer(9999) + JSONRPC() + HelloWorld()).run()
