# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

import pytest

from time import sleep
from collections import deque

from circuits.core.manager import TIMEOUT
from circuits import handler, BaseComponent, Debugger, Manager


class Watcher(BaseComponent):

    def init(self):
        self.events = deque([], 10)

    @handler(channel="*", priority=999.9)
    def _on_event(self, event, *args, **kwargs):
        self.events.append(event)

    def wait(self, name, channel=None, timeout=3.0):
        for i in range(int(timeout / TIMEOUT)):
            if channel is None:
                for event in self.events:
                    if event.name == name:
                        return True
            else:
                for event in self.events:
                    if event.name == name and channel in event.channels:
                        return True
            sleep(TIMEOUT)


@pytest.fixture(scope="session")
def manager(request):
    manager = Manager()

    def finalizer():
        manager.stop()

    request.addfinalizer(finalizer)

    if request.config.option.verbose:
        Debugger().register(manager)

    manager.start()

    return manager


@pytest.fixture(scope="session")
def watcher(request, manager):
    watcher = Watcher().register(manager)

    def finalizer():
        watcher.unregister()

    return watcher
