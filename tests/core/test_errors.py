#!/usr/bin/env python
import pytest

from circuits import Component, Event


class test(Event):

    """test Event"""


class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.etype = None
        self.evalue = None
        self.etraceback = None
        self.handler = None
        self.fevent = None

    def test(self):
        return x  # NOQA

    def exception(self, etype, evalue, etraceback, handler=None, fevent=None):
        self.etype = etype
        self.evalue = evalue
        self.etraceback = etraceback
        self.handler = handler
        self.fevent = fevent


def reraise(e):
    raise e


@pytest.fixture
def app(request, manager, watcher):
    app = App().register(manager)
    watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_main(app, watcher):
    e = test()
    app.fire(e)
    watcher.wait("exception")

    assert app.etype == NameError
    pytest.raises(NameError, lambda e: reraise(e), app.evalue)
    assert isinstance(app.etraceback, list)
    assert app.handler == app.test
    assert app.fevent == e
