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


def test_pass_class():
    assert IO.handles("read", "write")


def test_fail_class():
    assert not App.handles("read", "write")


def test_pass_instance():
    assert IO().handles("read", "write")


def test_fail_instance():
    assert not App().handles("read", "write")
