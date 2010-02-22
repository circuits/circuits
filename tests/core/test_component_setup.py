# Module:   test_component_setup
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Component Setup Tests

Tests that filters and listeners of a Component are
automatically registered as event handlers.
"""

from circuits import Component, Manager

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

def test():
    m = Manager()

    app = App()
    app.register(m)

    assert app.test in m.channels.get(("*", "test"), [])

    app.unregister()

    assert not m._handlers
