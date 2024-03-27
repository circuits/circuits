"""Lightweight Event driven and Asynchronous Application Framework

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

:copyright: CopyRight (C) 2004-2016 by James Mills
:license: MIT (See: LICENSE)

.. _Python Programming Language: http://www.python.org/
"""

__author__ = 'James Mills'
__date__ = '24th February 2013'

try:
    from .version import version as __version__
except ImportError:
    __version__ = 'unknown'

from .core import (
    BaseComponent,
    Bridge,
    Component,
    Debugger,
    Event,
    Loader,
    Manager,
    TimeoutError,
    Timer,
    Worker,
    handler,
    ipc,
    reprhandler,
    sleep,
    task,
)


# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    import importlib.metadata

    try:
        namespace_pkg = importlib.metadata.distribution(__name__)
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        namespace_pkg.activate()

# flake8: noqa
# pylama:skip=1
