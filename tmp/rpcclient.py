#!/usr/bin/python -i

import xmlrpclib
import jsonrpclib

url = "http://127.0.0.1:9999/rpc/"

#xmlrpc = xmlrpclib.ServerProxy(url, allow_none=True)
jsonrpc = jsonrpclib.ServerProxy(url, allow_none=True)
