#!/usr/bin/env python
import os

import pytest

from circuits import Component, handler

try:
    from circuits.io.notify import Notify
except ImportError:
    pytest.importorskip("pyinotify")


class App(Component):

    def init(self, *args, **kwargs):
        self.created_status = False

    @handler('created', channel='notify')
    def created(self, *args, **kwargs):
        self.created_status = True


class Creator:

    def __init__(self, app, watcher, tmpdir, timeout=0.5):
        self.app = app
        self.watcher = watcher
        self.tmpdir = tmpdir
        self.timeout = timeout

    def create(self, *targets, **kwargs):
        assert_created = kwargs.get('assert_created', True)
        target = os.path.join(*targets)
        self.tmpdir.ensure(target, dir=kwargs.get('dir', False))
        self.watcher.wait("created", timeout=self.timeout)
        assert self.app.created_status == assert_created
        # Reset for next call
        self.watcher.clear()
        self.app.created_status = False


@pytest.fixture()
def app(manager, watcher):
    app = App().register(manager)
    yield app
    # Unregister application on test end
    app.unregister()
    watcher.wait("unregistered")


@pytest.fixture()
def notify(app, watcher):
    notify = Notify().register(app)
    watcher.wait("registered")
    return notify


@pytest.fixture()
def creator(app, watcher, tmpdir):
    return Creator(app, watcher, tmpdir)


# TESTS


def test_notify_file(notify, tmpdir, creator):

    # Add a path to the watch
    notify.add_path(str(tmpdir))

    # Test creation and detection of a file
    creator.create("helloworld.txt")

    # Remove the path from the watch
    notify.remove_path(str(tmpdir))

    # Test creation and NON detection of a file
    creator.create("helloworld2.txt", assert_created=False)


def test_notify_dir(notify, tmpdir, creator):

    # Add a path to the watch
    notify.add_path(str(tmpdir))

    # Test creation and detection of a file
    creator.create("hellodir", dir=True)

    # Remove the path from the watch
    notify.remove_path(str(tmpdir))

    # Test creation and NON detection of a file
    creator.create("hellodir2", dir=True, assert_created=False)


def test_notify_subdir_recursive(notify, tmpdir, creator):

    # Add a subdir
    subdir = "sub"
    tmpdir.ensure(subdir, dir=True)

    # Add a path to the watch
    notify.add_path(str(tmpdir), recursive=True)

    # Test creation and detection of a file in subdir
    creator.create(subdir, "helloworld.txt", assert_created=True)


@pytest.mark.xfail(reason="pyinotify issue #133")
def test_notify_subdir_recursive_remove_path(notify, tmpdir, creator):
    # This is logically the second part of the above test,
    # but pyinotify fails on rm_watch(...., rec=True)

    # Add a subdir
    subdir = "sub"
    tmpdir.ensure(subdir, dir=True)

    # Add a path to the watch
    notify.add_path(str(tmpdir), recursive=True)

    # Remove the path from the watch
    notify.remove_path(str(tmpdir), recursive=True)

    # Test creation and NON detection of a file in subdir
    creator.create(subdir, "helloworld2.txt", assert_created=False)


def test_notify_subdir_recursive_auto_add(notify, tmpdir, creator):

    # Add a path to the watch
    notify.add_path(str(tmpdir), recursive=True)

    # Create/detect subdirectory
    subdir = "sub"
    creator.create(subdir, dir=True, assert_created=True)

    # Create/detect file in subdirectory
    creator.create(subdir, "helloworld.txt", assert_created=True)

    # Skip notify.remove_path() because pyinotify is broken


def test_notify_subdir_recursive_no_auto_add(notify, tmpdir, creator):

    # Add a path to the watch
    notify.add_path(str(tmpdir), recursive=True, auto_add=False)

    # Create/detect subdirectory
    subdir = "sub"
    creator.create(subdir, dir=True, assert_created=True)

    # Create, not detect file in subdirectory
    creator.create(subdir, "helloworld.txt", assert_created=False)

    # Skip notify.remove_path() because pyinotify is broken
