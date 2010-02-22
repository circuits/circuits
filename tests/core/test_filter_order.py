# Module:   test_filter_order
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Filter Order Tests

Test that Event Handlers set as Filters are added and sorted
such that Filters preceed non-filters.
"""

from circuits import handler, Component


class App(Component):

    def test(self, event, *args, **kwargs):
        pass

    @handler("test", filter=True)
    def on_test(self, event, *args, **kwargs):
        pass

def test():
    app = App()
    handlers = app.channels.get(("*", "test"), [])
    assert handlers and handlers[0] == app.on_test
