#!/usr/bin/python -i

"""Bridge Example

To use this example run it interactively through the Python interactive
shell using the -i option as per the shebang line above.

i.e: python -i hello_bridge.py

At the python prompt:

    >>> x = m.fire(Hello())
    .
    .
    .
    >>> x
    <Value ('Hello World! (15969)') result: True errors: False for <Hello[*.hello] ( )>
"""  # noqa


from os import getpid


from circuits import Component, Debugger, Event, Manager


class hello(Event):
    """hello Event"""


class App(Component):

    def hello(self):
        return "Hello World! ({0:d})".format(getpid())


m = Manager() + Debugger()
m.start()
App().start(process=True, link=m)
