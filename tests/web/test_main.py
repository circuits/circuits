#!/usr/bin/env python

import pytest

from time import sleep
from threading import Thread
from errno import ECONNREFUSED
from subprocess import Popen

from circuits.net.sockets import UDPServer, Close

from .helpers import urlopen, URLError, HTTPError

SERVER_CMD = ["python", "-m", "circuits.web.main"]


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


class Server(Thread):

    def __init__(self, *args):
        super(Server, self).__init__()

        self.args = list(args)

        self.setDaemon(True)

    def run(self):
        self.process = Popen(SERVER_CMD + self.args)

    def stop(self):
        self.process.terminate()
        self.process.wait()


def test():
    port = find_free_port()

    server = Server("-b", "0.0.0.0:%d" % port)
    server.start()

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

    server.stop()
