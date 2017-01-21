#!/usr/bin/env python
from circuits import BaseComponent, Event, handler


class test(Event):

    """test Event"""


class App(BaseComponent):

    @handler("test")
    def _on_test(self, event):
        try:
            return "Hello World!"
        finally:
            event.stop()

    def _on_test2(self):
        pass  # Never reached


def test_main():
    app = App()
    while len(app):
        app.flush()
    x = app.fire(test())
    app.flush()
    assert x.value == "Hello World!"
