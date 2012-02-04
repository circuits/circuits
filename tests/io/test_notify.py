import pytest
pytest.importorskip("pyinotify")

from circuits.io.notify import Notify, AddPath, RemovePath
from circuits import Component, handler


class App(Component):

    def __init__(self, *args, **kwargs):
        super(App, self).__init__()
        self.add_path = False
        self.remove_path = False
        self.created = False

    def add_path(self, path):
        self.add_path = True

    def remove_path(self, path):
        self.remove_path = True

    @handler('created', channel='notify')
    def created(self, *args, **kwargs):
        self.created = True

def test_notify(tmpdir):
    app = App()
    Notify().register(app)
    app.start()
    try:
        app.fire(AddPath(str(tmpdir)))
        pytest.wait_for(app, 'add_path')
        tmpdir.ensure("helloworld.txt")
        assert pytest.wait_for(app, 'created')
        app.created = False
        app.fire(RemovePath(str(tmpdir)))
        pytest.wait_for(app, 'remove_path')
        tmpdir.ensure("helloworld2.txt")
        assert not pytest.wait_for(app, 'created')
    finally:
        app.stop()

    assert True
