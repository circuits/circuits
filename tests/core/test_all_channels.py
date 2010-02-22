# Module:   test_all_channels
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""All Channels Tests

Test that events can be sent to all channels.
"""

from circuits import Event, Component, Manager

class Base(Component):

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

        self.flag = False

    def foo(self, event, *args, **kwargs):
        self.flag = True

def test():
    m = Manager()
    a = Base(channel="a")
    b = Base(channel="b")
    c = Base()

    a.register(m)
    b.register(m)
    c.register(m)

    while m:
        m.flush()

    m.push(Event(), "*")
    m.flush()

    assert not a.flag
    assert not b.flag
    assert c.flag
