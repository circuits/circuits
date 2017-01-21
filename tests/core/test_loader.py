#!/usr/bin/env python
from os.path import dirname

import pytest

from circuits import Event, Loader, Manager


class test(Event):

    """test Event"""


def test_main():
    m = Manager()
    loader = Loader(paths=[dirname(__file__)]).register(m)

    m.start()

    loader.load("app")

    x = m.fire(test())

    assert pytest.wait_for(x, "result")

    s = x.value
    assert s == "Hello World!"

    m.stop()
