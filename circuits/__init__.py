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
    import sys

    try:
        namespace_pkg = importlib.metadata.distribution(__name__)
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        namespace_pkg_files = namespace_pkg.files
        if namespace_pkg_files:
            for file in namespace_pkg_files:
                if str(file).endswith('__init__.py'):
                    namespace_pkg_path = str(file).split('__init__.py')[0]
                    if namespace_pkg_path not in sys.path:
                        sys.path.append(namespace_pkg_path)
                    break

# flake8: noqa
# pylama:skip=1
