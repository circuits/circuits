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

    waiter = pytest.WaitEvent(env, "create_success")
    env.fire(Create())
    assert waiter.wait()

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)


def test_load(env, path):
    from circuits.app.env import Create, Load

    waiter = pytest.WaitEvent(env, "create_success")
    env.fire(Create())

    assert waiter.wait()

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    waiter = pytest.WaitEvent(env, "load_success")
    env.fire(Load())

    assert waiter.wait()


def test_load_verify(env, path):
    from circuits.app.env import Create, Load

    waiter = pytest.WaitEvent(env, "create_success")
    env.fire(Create())

    assert waiter.wait()

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    waiter = pytest.WaitEvent(env, "load_success")
    env.fire(Load(verify=True))

    assert waiter.wait()


def test_load_verify_fail(env, path):
    from circuits.app.env import Create, Load
    from circuits.app.env import EnvironmentError, ERRORS

    waiter = pytest.WaitEvent(env, "create_success")
    env.fire(Create())

    assert waiter.wait()

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    path.join("VERSION").write("")

    waiter = pytest.WaitEvent(env, "verify_failure")
    v = env.fire(Load(verify=True))

    assert waiter.wait()

    assert isinstance(v[1], EnvironmentError)
    assert v[1].args == ERRORS[0]


def test_load_verify_upgrade(env, path):
    from circuits.app.env import Create, Load
    from circuits.app.env import EnvironmentError, ERRORS

    waiter = pytest.WaitEvent(env, "create_success")
    env.fire(Create())

    assert waiter.wait()

    files = ("conf/test.ini", "README", "VERSION")

    for filename in files:
        assert path.join(filename).check(exists=True, file=True)

    env.version = 100

    waiter = pytest.WaitEvent(env, "verify_failure")
    v = env.fire(Load(verify=True))

    assert waiter.wait()

    assert isinstance(v[1], EnvironmentError)
    assert v[1].args == ERRORS[1]
