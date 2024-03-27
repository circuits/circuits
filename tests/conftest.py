"""py.test config."""

import sys
import threading
from collections import deque
from collections.abc import Callable
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

    def clear(self) -> None:
        self.events.clear()

    def wait(self, name, channel=None, timeout=30.0) -> bool:
        for _i in range(int(timeout / TIMEOUT)):
            with self._lock:
                for event in self.events:
                    if event.name == name and event.waitingHandlers == 0 and ((channel is None) or (channel in event.channels)):
                        return True
            sleep(TIMEOUT)
        return False

    def count(self, name, channel=None, n=1, timeout=30.0):
        n = 0
        with self._lock:
            for event in self.events:
                if event.name == name and event.waitingHandlers == 0 and ((channel is None) or (channel in event.channels)):
                    n += 1
        return n


class Flag:
    status = False


def call_event_from_name(manager, event, event_name, *channels):
    fired = False
    value = None
    for _r in manager.waitEvent(event_name):
        if not fired:
            fired = True
            value = manager.fire(event, *channels)
        sleep(0.1)
    return value


def call_event(manager, event, *channels):
    return call_event_from_name(manager, event, event.name, *channels)


class WaitEvent:
    def __init__(self, manager, name, channel=None, timeout=30.0) -> None:
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


def wait_for(obj, attr, value=True, timeout=30.0) -> Optional[bool]:
    from circuits.core.manager import TIMEOUT

    for _i in range(int(timeout / TIMEOUT)):
        if isinstance(value, Callable):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)
    return None


class SimpleManager(Manager):
    def tick(self, timeout=-1):
        self._running = False
        return super().tick(timeout)


@pytest.fixture()
def simple_manager(request):
    manager = SimpleManager()
    Debugger(events=request.config.option.verbose).register(manager)
    return manager


@pytest.fixture()
def manager(request):
    manager = Manager()

    def finalizer() -> None:
        manager.stop()

    request.addfinalizer(finalizer)

    waiter = WaitEvent(manager, 'started')
    manager.start()
    assert waiter.wait()

    Debugger(events=request.config.option.verbose).register(manager)

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


for key, value in {
    'WaitEvent': WaitEvent,
    'wait_for': wait_for,
    'call_event': call_event,
    'PLATFORM': sys.platform,
    'PYVER': sys.version_info[:3],
    'call_event_from_name': call_event_from_name,
}.items():
    setattr(pytest, key, value)
