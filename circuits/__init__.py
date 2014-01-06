# Package:  circuits
# Date:     3rd October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Lightweight Event driven and Asynchronous Application Framework

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

:copyright: CopyRight (C) 2004-2013 by James Mills
:license: MIT (See: LICENSE)

.. _Python Programming Language: http://www.python.org/
"""

__author__ = "James Mills"
__date__ = "24th February 2013"

from circuits.core import Event
from circuits.core import task, Worker
from circuits.version import version as __version__
from circuits.core import handler, reprhandler, BaseComponent, Component
from circuits.core import Debugger, Bridge, Loader, Manager, Timer, TimeoutError

# flake8: noqa
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
