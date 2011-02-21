#!/usr/bin/env python

import pytest

from circuits import Manager
from circuits.core.utils import itercmp
from circuits.core.pollers import BasePoller, Poller
from circuits.net.sockets import TCPServer, TCPClient

def test():
    m = Manager()

    poller = Poller().register(m)

    TCPServer(0).register(m)
    TCPClient().register(m)

    m.start()

    try:
        pollers = list(itercmp(m, BasePoller, subclass=False))
        assert len(pollers) == 1
        assert pollers[0] is poller
    finally:
        m.stop()
