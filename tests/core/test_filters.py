#!/usr/bin/env python

from circuits import handler, Event, BaseComponent

class Test(Event):
    """Test Event"""

class App(BaseComponent):

    @handler("test", filter=True)
    def _on_test(self):
        return "Hello World!"

    def _on_test2(self):
        pass # Never reached

def test():
    app = App()
    while app: app.flush()
    x = app.push(Test())
    app.flush()
    assert x.value == "Hello World!"
