#!/usr/bin/env python
"""
Test Interface Query.

Test the capabilities of querying a Component class or instance for it's
interface. That is it's event handlers it responds to.
"""

from circuits import Component


class Base(Component):
    def foo(self) -> None:
        pass


class SuperBase(Base):
    def bar(self) -> None:
        pass


def test_handles_base_class() -> None:
    assert Base.handles('foo')


def test_handles_super_base_class() -> None:
    assert SuperBase.handles('foo', 'bar')


def test_handles_base_instance() -> None:
    base = Base()
    assert base.handles('foo')


def test_handles_super_base_instance() -> None:
    superbase = SuperBase()
    assert superbase.handles('foo', 'bar')
