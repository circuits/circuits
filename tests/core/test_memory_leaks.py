import pytest


import resource


from circuits import Event, Component


ITERATIONS = 1000


class test(Event):
    """test Event"""


class test_call(Event):
    """test Event"""


class App(Component):

    def test(self):
        return "Hello World!"

    def test_call(self):
        for _ in range(ITERATIONS):
            yield self.call(test())

    @property
    def memory(self):
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


@pytest.fixture()
def app(request):
    app = App()

    def finalizer():
        app.stop()

    request.addfinalizer(finalizer)

    app.start()

    return app


def test_memory_call(app):
    start_memory = app.memory
    event = test_call()

    for _ in range(ITERATIONS):
        for _ in app.call(event):
            pass

    assert app.memory == start_memory


def test_memory_fire(app):
    start_memory = app.memory

    for _ in range(ITERATIONS):
        app.fire(test())

    while len(app):
        pass

    assert app.memory == start_memory


def test_memory_wait(app):
    start_memory = app.memory
    event = test()

    for _ in range(ITERATIONS):
        for _ in app.waitEvent(event):
            pass

    assert app.memory == start_memory
