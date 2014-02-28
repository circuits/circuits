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

from .version import version as __version__

from .core import Event
from .core import task, Worker
from .core import handler, reprhandler, BaseComponent, Component
from .core import Debugger, Bridge, Loader, Manager, Timer, TimeoutError

# flake8: noqa
