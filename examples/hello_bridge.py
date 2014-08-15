#!/usr/bin/env python


"""Bridge Example

Should display:

- foo <pid>
. bar <pid>

Where <pid> is the parent and child process id respectively.y
"""


from __future__ import print_function

from os import getpid


from circuits import Component, Event


class foo(Event):
    """foo Event"""


class bar(Event):
    """bar Event"""


class App(Component):

    def foo(self):
        return "foo ({0:d})".format(getpid())

    def started(self, *args):
        x = yield self.call(foo())
        print(x.value)

        y = yield self.call(bar())
        print(y.value)

        raise SystemExit(0)


class SubApp(Component):

    def bar(self):
        return "bar ({0:d})".format(getpid())


app = App()
SubApp().start(process=True, link=app)
app.run()
