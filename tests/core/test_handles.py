#!/usr/bin/env python


from circuits import Component


class IO(Component):

    def read(self, data):
        pass

    def write(self, data):
        pass


class App(Component):

    def hello(self):
        pass


def test_pass():
    assert IO.handles("read", "write")


def test_fail():
    assert not App.handles("read", "write")
