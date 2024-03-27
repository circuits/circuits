#!/usr/bin/env python
from typing import NoReturn

import pytest

from circuits import Component, Event


class test(Event):
    """test Event."""


class App(Component):
    def __init__(self) -> None:
        super().__init__()

        self.etype = None
        self.evalue = None
        self.etraceback = None
        self.handler = None
        self.fevent = None

    def test(self):
        return x  # noqa: F821

    def exception(self, etype, evalue, etraceback, handler=None, fevent=None) -> None:
        self.etype = etype
        self.evalue = evalue
        self.etraceback = etraceback
        self.handler = handler
        self.fevent = fevent


def reraise(e) -> NoReturn:
    raise e


@pytest.fixture()
def app(request, manager, watcher):
    app = App().register(manager)
    watcher.wait('registered')

    def finalizer() -> None:
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_main(app, watcher) -> None:
    e = test()
    app.fire(e)
    watcher.wait('exception')

    assert app.etype == NameError
    pytest.raises(NameError, reraise, app.evalue)
    assert isinstance(app.etraceback, list)
    assert app.handler == app.test
    assert app.fevent == e
