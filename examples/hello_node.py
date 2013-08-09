#!/usr/bin/python -i

"""Node Example

To use this example run it interactively through the Python interactive shell
using the -i option as per the shebang line above.

i.e: python -i hello_node.py

At the python prompt:

    >>> x = app1.fire(Hello())
    >>> <Hello[*.hello] ( )>

    >>> x
    <Value ('Hello World! (16030)') result: True errors: False for <Hello[*.hello] ( )>
    >>> y = app1.fire(Remote(Hello(), "app2"))
    .
    .
    .
    >>> y
    <Value (u'Hello World! (16035)') result: True errors: False for <Remote[*.remote] (<Hello[.hello] ( )>, 'app2' channel=None)>
"""


from os import getpid

from circuits.node import Node, Remote
from circuits import Component, Debugger, Event


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        return "Hello World! ({0:d})".format(getpid())


# Setup app1 with a debugger
app1 = App() + Debugger()
node1 = Node().register(app1)

# Our 2nd app is going to bind itself to tcp://127.0.0.1:9000
bind = ("127.0.0.1", 9000)

# Setup app2 and bind the Node to tcp://127.0.0.1:9000
app2 = App()
node2 = Node(bind).register(app2)

# Start app2 as a separate process
app2.start(process=True)

# Register app2's address to node1 so we can talk to it
node1.add("app2", *bind)

# Start app1 as a thread
app1.start()

# flake8: noqa
