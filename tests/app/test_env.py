#!/usr/bin/env python

import pytest


def pytest_funcarg__path(request):
    tmpdir = request.getfuncargvalue("tmpdir")
    return tmpdir.join("env")


def pytest_funcarg__env(request):
    return request.cached_setup(
            setup=lambda: setup_env(request),
            teardown=lambda env: teardown_env(env),
            scope="function")


def setup_env(request):
    from circuits.app.env import Environment

    path = request.getfuncargvalue("path")

    env = Environment(str(path), "test")

    env.start()

    return env


def teardown_env(env):
    env.stop()


def test_create(env, path):
    from circuits.app.env import Create

    env.push(Create())
    assert pytest.wait_event(env, "create_success")

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)


def test_load(env, path):
    from circuits.app.env import Create, Load

    env.push(Create())

    assert pytest.wait_event(env, "create_success")

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    env.push(Load())

    assert pytest.wait_event(env, "load_success")


def test_load_verify(env, path):
    from circuits.app.env import Create, Load

    env.push(Create())

    assert pytest.wait_event(env, "create_success")

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    env.push(Load(verify=True))

    assert pytest.wait_event(env, "load_success")


def test_load_verify_fail(env, path):
    from circuits.app.env import Create, Load
    from circuits.app.env import EnvironmentError, ERRORS

    env.push(Create())

    assert pytest.wait_event(env, "create_success")

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    path.join("VERSION").write("")

    v = env.push(Load(verify=True))

    assert pytest.wait_event(env, "verify_failure")

    assert isinstance(v[1], EnvironmentError)
    assert v[1].args == ERRORS[0]


def test_load_verify_upgrade(env, path):
    from circuits.app.env import Create, Load
    from circuits.app.env import EnvironmentError, ERRORS

    env.push(Create())

    assert pytest.wait_event(env, "create_success")

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    env.version = 100

    v = env.push(Load(verify=True))

    assert pytest.wait_event(env, "verify_failure")

    assert isinstance(v[1], EnvironmentError)
    assert v[1].args == ERRORS[1]
