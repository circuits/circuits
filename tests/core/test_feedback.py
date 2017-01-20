"""Feedback Channels Tests"""

import py

from circuits import Component, Event, handler


class test(Event):

    """test Event"""

    success = True
    failure = True


class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.e = None
        self.error = None
        self.value = None
        self.success = False
        self.failure = False

    @handler("*")
    def event(self, event, *args, **kwargs):
        if kwargs.get("filter", False):
            event.stop()

    def test(self, error=False):
        if error:
            raise Exception("Hello World!")

        return "Hello World!"

    def test_success(self, e, value):
        self.e = e
        self.value = value
        self.success = True

    def test_failure(self, e, error):
        self.e = e
        self.error = error
        self.failure = True


def reraise(e):
    raise e


def test_success():
    app = App()
    while len(app):
        app.flush()

    e = test()
    value = app.fire(e)

    while len(app):
        app.flush()

    # The Event
    s = value.value
    assert s == "Hello World!"

    while len(app):
        app.flush()

    assert app.e == e
    assert app.success
    assert app.e.value == value
    assert app.value == value.value


def test_failure():
    app = App()
    while len(app):
        app.flush()

    e = test(error=True)
    x = app.fire(e)

    while len(app):
        app.flush()

    # The Event
    py.test.raises(Exception, lambda x: reraise(x[1]), x.value)

    while len(app):
        app.flush()

    assert app.e == e

    etype, evalue, etraceback = app.error
    py.test.raises(Exception, lambda x: reraise(x), evalue)
    assert etype == Exception

    assert app.failure
    assert not app.success
    assert app.e.value == x
