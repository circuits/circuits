# Module:   test_feedback
# Date:     11th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Feedback Channels Tests"""

import py

from circuits import handler, Event, Component


class Test(Event):
    """Test Event"""

    success = True
    failure = True

class Test2(Event):
    end = True


class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.e = None
        self.success = False
        self.failure = False
        self.end = False
        self.failed_end = False

    @handler("*", filter=True)
    def event(self, event, *args, **kwargs):
        if kwargs.get("filter", False):
            return True

    def test(self, error=False):
        if error:
            raise Exception("Hello World!")

        return "Hello World!"

    def test2(self):
        if self.end:
            self.failed_end = True

    @handler("test2")
    def test22(self):
        return self.test2(self)


    def test2_end(self, e):
        self.e = e
        if not self.failed_end:
            self.end = True

    def test_success(self, e):
        self.e = e
        self.success = True

    def test_failure(self, e):
        self.e = e
        self.failure = True


def reraise(e):
    raise e


def test_end():
    app = App()
    while app:
        app.flush()

    e = Test2()
    x = app.fire(e)

    while app:
        app.flush()

    assert app.e == e
    assert app.end


def test_success():
    app = App()
    while app:
        app.flush()

    e = Test()
    x = app.fire(e)

    while app:
        app.flush()

    # The Event
    s = x.value
    assert s == "Hello World!"

    while app:
        app.flush()

    assert app.e == e
    assert app.success
    assert app.e.value == x


def test_failure():
    app = App()
    while app:
        app.flush()

    e = Test(error=True)
    x = app.fire(e)

    while app:
        app.flush()

    # The Event
    py.test.raises(Exception, lambda x: reraise(x[1]), x.value)

    while app:
        app.flush()

    assert app.e == e
    assert app.failure
    assert not app.success
    assert app.e.value == x
