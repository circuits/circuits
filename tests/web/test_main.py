#!/usr/bin/env python

from time import sleep
from threading import Thread
from errno import ECONNREFUSED
from subprocess import Popen, PIPE

from .helpers import urlopen, URLError, HTTPError

SERVER_CMD = ["python", "-m", "circuits.web.main"]


class Server(Thread):

    def __init__(self):
        super(Server, self).__init__()

        self.setDaemon(True)

    def run(self):
        self.process = Popen(SERVER_CMD)

    def stop(self):
        self.process.terminate()
        self.process.wait()


def test():
    server = Server()
    server.start()

    sleep(1)

    f = None

    for _ in range(3):
        try:
            f = urlopen("http://127.0.0.1:8000/hello")
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
