# Module:   test_filter_order
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Filter Order Tests

Test that Event Handlers set as Filters are added and sorted
such that Filters preceed non-filters.
"""

from circuits import handler, Component, Event

class Test(Event):
    pass


class App(Component):
    def __init__(self):
        super(App, self).__init__()
        self.events_executed = []

    def test(self, event, *args, **kwargs):
        self.events_executed.append('test')

    @handler("test", filter=True)
    def on_test(self, event, *args, **kwargs):
        self.events_executed.append('test_filter')
        return True

def test():
    app = App()
    app.fire(Test())
    while app:
        app.flush()
    assert app.events_executed == ['test_filter']
