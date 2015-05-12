#!/usr/bin/python -i

import pytest

from circuits import Event, Component


class test(Event):
    """test Event"""


class coroutine1(Event):
    """coroutine Event"""


class coroutine2(Event):
    """coroutine Event"""


class App(Component):

    returned = False

    def test(self, event):
        event.stop()
        return "Hello World!"

    def coroutine1(self):
        print('coroutine1')
        yield self.call(test())
        print 'returned'
        self.returned = True

    def coroutine2(self):
        print('coroutine2')
        yield self.wait(self.fire(test()))
        print 'returned'
        self.returned = True


@pytest.fixture(scope="module")
def app(request, manager, watcher):
    app = App().register(manager)
    assert watcher.wait("registered")

    def finalizer():
        app.unregister()

    request.addfinalizer(finalizer)

    return app


def test_coroutine(manager, watcher, app):
    manager.fire(coroutine1())
    assert watcher.wait('coroutine1')
    assert app.returned, 'coroutine1'
    app.returned = False
    manager.fire(coroutine2())
    assert watcher.wait('coroutine2')
    assert app.returned, 'coroutine2'
