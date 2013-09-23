#!/usr/bin/env python

from circuits import handler, Event, BaseComponent


class test(Event):
    """test Event"""


class App(BaseComponent):

    @handler("test", filter=True)
    def _on_test(self):
        return "Hello World!"

    def _on_test2(self):
        pass  # Never reached


def test_main():
    app = App()
    while app:
        app.flush()
    x = app.fire(test())
    app.flush()
    assert x.value == "Hello World!"
