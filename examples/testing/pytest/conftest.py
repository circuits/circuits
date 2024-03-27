"""py.test config."""

import sys
import threading
from collections import deque
from time import sleep
from typing import Optional

import pytest

from circuits import BaseComponent, Debugger, Manager, handler
from circuits.core.manager import TIMEOUT


class Watcher(BaseComponent):
    def init(self) -> None:
        self._lock = threading.Lock()
        self.events = deque()

    @handler(channel='*', priority=999.9)
    def _on_event(self, event, *args, **kwargs) -> None:
        with self._lock:
            self.events.append(event)

    def wait(self, name, channel=None, timeout=6.0) -> Optional[bool]:
        for _i in range(int(timeout / TIMEOUT)):
            if channel is None:
                with self._lock:
                    for event in self.events:
                        if event.name == name:
                            return True
            else:
                with self._lock:
                    for event in self.events:
                        if event.name == name and channel in event.channels:
                            return True

            sleep(TIMEOUT)
        return None


class Flag:
    status = False


class WaitEvent:
    def __init__(self, manager, name, channel=None, timeout=6.0) -> None:
        if channel is None:
            channel = getattr(manager, 'channel', None)

        self.timeout = timeout
        self.manager = manager

        flag = Flag()

        @handler(name, channel=channel)
        def on_event(self, *args, **kwargs) -> None:
            flag.status = True

        self.handler = self.manager.addHandler(on_event)
        self.flag = flag

    def wait(self) -> Optional[bool]:
        try:
            for _i in range(int(self.timeout / TIMEOUT)):
                if self.flag.status:
                    return True
                sleep(TIMEOUT)
        finally:
            self.manager.removeHandler(self.handler)


@pytest.fixture(scope='session')
def manager(request):
    manager = Manager()

    def finalizer() -> None:
        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, 'started')
    manager.start()
    assert waiter.wait()

    if request.config.option.verbose:
        Debugger().register(manager)

    return manager


@pytest.fixture()
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer() -> None:
        waiter = WaitEvent(manager, 'unregistered')
        watcher.unregister()
        waiter.wait()

    request.addfinalizer(finalizer)

    return watcher


for key, value in {'WaitEvent': WaitEvent, 'PLATFORM': sys.platform, 'PYVER': sys.version_info[:3]}.items():
    setattr(pytest, key, value)
