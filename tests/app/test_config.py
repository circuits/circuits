#!/usr/bin/env python

import pytest

from circuits.app.config import Config, Load


CONFIG = """\
[test]
foo = bar
int = 1
float = 1.0
bool = 1
"""


@pytest.fixture(scope="function")
def config_file(tmpdir):
    f = tmpdir.ensure("test.ini")
    f.write(CONFIG)
    return str(f)


@pytest.fixture(scope="function")
def config(request, manager, watcher, config_file):
    config = Config(config_file).register(manager)

    def finalizer():
        config.unregister()

    request.addfinalizer(finalizer)

    manager.fire(Load(), config.channel)
    flag = watcher.wait("load_success")
    assert flag

    # This ensures the tests pass. WTF?!
    from time import sleep
    sleep(0.1)

    return config


def test_add_section(config):
    config.add_section("foo")
    has_foo = config.has_section("foo")
    assert has_foo


def test_has_section(config):
    has_test = config.has_section("test")
    assert has_test


def test_get(config):
    foo = config.get("test", "foo")
    assert foo == "bar"

    asdf = config.get("test", "asdf", "foobar")
    assert asdf == "foobar"


def test_get_int(config):
    one = config.getint("test", "int")
    assert one == 1

    ottf = config.getint("test", "asdf", 1234)
    assert ottf == 1234


def test_get_float(config):
    opz = config.getfloat("test", "float")
    assert opz == 1.0

    ottfpottf = config.getfloat("test", "asdf", 1234.1234)
    assert ottfpottf == 1234.1234


def test_get_bool(config):
    boolean = config.getboolean("test", "bool")
    assert boolean

    asdf = config.getboolean("test", "asdf", False)
    assert not asdf
