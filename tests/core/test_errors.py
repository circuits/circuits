#!/usr/bin/env python
import pytest

from circuits import Component, Event


class test(Event):

    """test Event"""


class App(Component):

    def __init__(self):
        super().__init__()

        self.etype = None
        self.evalue = None
        self.etraceback = None
        self.handler = None
        self.fevent = None

    def test(self):
        return x  # noqa: F821

    def exception(self, etype, evalue, etraceback, handler=None, fevent=None):
        self.etype = etype
        self.evalue = evalue
        self.etraceback = etraceback
        self.handler = handler
        self.fevent = fevent


def reraise(e):
    raise e


@pytest.fixture
def app(simple_manager):
    return App().register(simple_manager)


def test_main(app, simple_manager):
    e = test()
    app.fire(e)
    assert simple_manager.run_until("exception")

    assert app.etype == NameError
    pytest.raises(NameError, lambda e: reraise(e), app.evalue)
    assert isinstance(app.etraceback, list)
    assert app.handler == app.test
    assert app.fevent == e
