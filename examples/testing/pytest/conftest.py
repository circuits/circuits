"""py.test config"""

import sys
import threading
from collections import deque
from time import sleep

import pytest

from circuits import BaseComponent, Debugger, Manager, handler
from circuits.core.manager import TIMEOUT


class Watcher(BaseComponent):

    def init(self):
        self._lock = threading.Lock()
        self.events = deque()

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        with self._lock:
            self.events.append(event)

    def wait(self, name, channel=None, timeout=6.0):
        for i in range(int(timeout / TIMEOUT)):
            if channel is None:
                with self._lock:
                    for event in self.events:
                        if event.name == name:
                            return True
            else:
                with self._lock:
                    for event in self.events:
                        if event.name == name and \
                                channel in event.channels:
                            return True

            sleep(TIMEOUT)


class Flag(object):
    status = False


class WaitEvent(object):

    def __init__(self, manager, name, channel=None, timeout=6.0):
        if channel is None:
            channel = getattr(manager, "channel", None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, *args, **kwargs):
            flag.status = True

        self.handler = self.manager.addHandler(on_event)
        self.flag = flag

    def wait(self):
        try:
            for i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


@pytest.fixture(scope="session")
def manager(request):
    manager = Manager()

    def finalizer():
        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, "started")
    manager.start()
    assert waiter.wait()

    if request.config.option.verbose:
        Debugger().register(manager)

    return manager


@pytest.fixture
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer():
        waiter = WaitEvent(manager, "unregistered")
        watcher.unregister()
        waiter.wait()

    request.addfinalizer(finalizer)

    return watcher


for key, value in dict((
    ("WaitEvent", WaitEvent),
    ("PLATFORM", sys.platform),
    ("PYVER", sys.version_info[:3]),
)).items():
    setattr(pytest, key, value)
