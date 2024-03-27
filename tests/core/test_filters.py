#!/usr/bin/env python
from typing import Optional

from circuits import BaseComponent, Event, handler


class test(Event):
    """test Event."""


class App(BaseComponent):
    @handler('test')
    def _on_test(self, event) -> Optional[str]:
        try:
            return 'Hello World!'
        finally:
            event.stop()

    def _on_test2(self) -> None:
        pass  # Never reached


def test_main() -> None:
    app = App()
    while len(app):
        app.flush()
    x = app.fire(test())
    app.flush()
    assert x.value == 'Hello World!'
