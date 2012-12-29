#!/usr/bin/env python

import pytest
pytest.skip("XXX: Broken")

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

    manager.fire(Load(), config)
    assert watcher.wait("load_success")

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
