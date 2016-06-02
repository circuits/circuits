"""Lightweight Event driven and Asynchronous Application Framework

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

:copyright: CopyRight (C) 2004-2016 by James Mills
:license: MIT (See: LICENSE)

.. _Python Programming Language: http://www.python.org/
"""

__author__ = "James Mills"
__date__ = "24th February 2013"

try:
    from .version import version as __version__
except ImportError:
    __version__ = "unknown"

from .core import Event
from .core import ipc, Bridge
from .core import sleep, task, Worker
from .core import handler, reprhandler, BaseComponent, Component
from .core import Debugger, Loader, Manager, Timer, TimeoutError

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
    import os
    for _path in __path__:
        _path = os.path.join(_path, '__init__.py')
        if _path != __file__ and os.path.exists(_path):
            from .six import exec_
            with open(_path) as fd:
                exec_(fd, globals())
    del os, extend_path, _path, fd, exec_

# flake8: noqa
# pylama:skip=1
