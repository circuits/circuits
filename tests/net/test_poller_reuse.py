#!/usr/bin/env python
from circuits import Manager
from circuits.core.pollers import BasePoller, Poller
from circuits.core.utils import findtype
from circuits.net.sockets import TCPClient, TCPServer


def test():
    m = Manager()

    poller = Poller().register(m)

    TCPServer(0).register(m)
    TCPClient().register(m)

    m.start()

    try:
        pollers = findtype(m, BasePoller, all=True)
        assert len(pollers) == 1
        assert pollers[0] is poller
    finally:
        m.stop()
