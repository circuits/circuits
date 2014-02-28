#!/usr/bin/env python


import pytest
pytest.importorskip("pyinotify")

from circuits.io.notify import Notify
from circuits import Component, handler


class App(Component):

    def init(self, *args, **kwargs):
        self.created = False

    @handler('created', channel='notify')
    def created(self, *args, **kwargs):
        self.created = True


def test_notify(manager, watcher, tmpdir):
    app = App().register(manager)
    notify = Notify().register(app)

    watcher.wait("registered")

    notify.add_path(str(tmpdir))

    tmpdir.ensure("helloworld.txt")
    watcher.wait("created")
    assert app.created
    app.created = False

    notify.remove_path(str(tmpdir))

    tmpdir.ensure("helloworld2.txt")
    watcher.wait("created")
    assert not app.created

    app.unregister()
    watcher.wait("unregistered")
