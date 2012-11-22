#!/usr/bin/env python

import pytest


CONFIG = """\
[test]
foo = bar
int = 1
float = 1.0
bool = 1
"""


def pytest_funcarg__config(request):
    from circuits.app.config import Config, Load

    tmpdir = request.getfuncargvalue("tmpdir")
    path = tmpdir.ensure("test.ini")
    path.write(CONFIG)

    config = Config(str(path))
    config.start()
    request.addfinalizer(lambda: config.stop())

    waiter = pytest.WaitEvent(config, "load_success")
    config.fire(Load())

    assert waiter.wait()

    return config


def test_add_section(config):
    config.add_section("foo")
    assert config.has_section("foo")


def test_has_section(config):
    assert config.has_section("test")


def test_get(config):
    s = config.get("test", "foo")
    assert s == "bar"

    s = config.get("test", "asdf", "foobar")
    assert s == "foobar"


def test_get_int(config):
    i = config.getint("test", "int")
    assert i == 1

    i = config.getint("test", "asdf", 1234)
    assert i == 1234


def test_get_float(config):
    f = config.getfloat("test", "float")
    assert f == 1.0

    f = config.getfloat("test", "asdf", 1234.1234)
    assert f == 1234.1234


def test_get_bool(config):
    b = config.getboolean("test", "bool")
    assert b

    b = config.getboolean("test", "asdf", False)
    assert not b


def test_load(tmpdir):
    from circuits.app.config import Config, Load

    path = tmpdir.ensure("test.ini")
    path.write(CONFIG)

    config = Config(str(path))
    config.start()

    waiter = pytest.WaitEvent(config, "load_success")
    config.fire(Load())

    assert waiter.wait()

    s = config.get("test", "foo")
    assert s == "bar"

    config.stop()


def test_save(tmpdir):
    from circuits.app.config import Config, Save

    path = tmpdir.ensure("test.ini")

    config = Config(str(path))
    config.start()

    config.add_section("test")
    config.set("test", "foo", "bar")

    waiter = pytest.WaitEvent(config, "save_success")
    config.fire(Save())

    assert waiter.wait()

    s = config.get("test", "foo")
    assert s == "bar"

    config.stop()
