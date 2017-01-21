#!/usr/bin/python -i
"""Node Example

To use this example run it interactively through the Python interactive
shell using the -i option as per the shebang line above.

i.e: python -i hello_node.py host port

At the python prompt:

    >>> x = app.fire(hello())
    >>> <Hello[*.hello] ( )>

    >>> x
    <Value ('Hello World! (16030)') result=True; errors=False; for <Hello[*.hello] ( )>
    >>> y = app.fire(remote(hello(), "test"))
    .
    .
    .
    >>> y
    <Value (u'Hello World! (16035)') result=True; errors=False; for <Remote[*.remote] (<Hello[.hello] ( )>, 'app2' channel=None)>
"""  # noqa
from __future__ import print_function

import sys
from os import getpid

from circuits import Component, Event
from circuits.node import Node, remote  # noqa


class hello(Event):

    """hello Event"""


class App(Component):

    def ready(self, client):
        print("Ready!")

    def connected(self, host, port):
        print("Connected to {}:{}".format(host, port))
        print("Try: x = app.fire(hello())")

    def hello(self):
        print("Now try: y = app.fire(remote(hello(), \"test\"))")
        return "Hello World! ({0:d})".format(getpid())


# Setup app1 with a debugger
app = App()
node = Node().register(app)

host = sys.argv[1]
port = int(sys.argv[2])
bind = (host, port)

# Add an address of a node to talk to called "test"
node.add("test", *bind)

# Start app as a thread
app.start()
