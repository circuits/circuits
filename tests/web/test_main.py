#!/usr/bin/env python

import pytest

from time import sleep
from subprocess import Popen
from errno import ECONNREFUSED

from circuits.net.sockets import UDPServer, Close

from .helpers import urlopen, URLError, HTTPError


def find_free_port():
    server = UDPServer(0)

    server.start()
    waiter = pytest.WaitEvent(server, "ready")
    waiter.wait()

    port = server.port

    server.fire(Close())
    waiter = pytest.WaitEvent(server, "disconnected")
    waiter.wait()

    server.stop()

    return port


def test():
    port = find_free_port()

    p = Popen(["python", "-m", "circuits.web.main", "-b", "0.0.0.0:%d" % port])

    sleep(1)

    f = None

    for _ in range(3):
        try:
            f = urlopen("http://127.0.0.1:%d/hello" % port)
            break
        except HTTPError as e:
            raise AssertionError(e)
        except URLError as e:
            if e.args[0][0] == ECONNREFUSED:
                sleep(1)
            else:
                raise AssertionError(e)

    assert f

    s = f.read()
    assert s == b"Hello World!"

    p.terminate()
    p.wait()
