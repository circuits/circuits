#!/usr/bin/env python

from circuits import handler, Event, Component, Debugger

class Test(Event):
    """Test Event"""

class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self._event = None

    def started(self, component, mode):
        if component == self:
            self.addHandler(handler("test")(self._test))

    def _test(self, event, *args, **kwargs):
        self._event = event

def test():
    app = App() + Debugger()

    #assert not app.running
    #assert app.state == "S"
    #assert app._event is None
    #assert len(app._handlers) == 1
    #assert len(app.channels) == 1

    app.start()

    from circuits.tools import inspect
    print inspect(app)

    #assert app.running
    #assert app.state == "R"
    #assert app._event is None
    #assert len(app._handlers) == 2
    #assert len(app.channels) == 2

    e = Test()
    app.push(e)

    while app: pass

    assert app._event == e
