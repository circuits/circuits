# Package:  core
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core

This package contains the essential core parts of the circuits framework.
"""


from .events import Event
from .bridge import Bridge
from .loader import Loader
from .manager import Manager, TimeoutError
from .handlers import handler, reprhandler
from .components import BaseComponent, Component

from .values import Value

from .timers import Timer

from .workers import task, Worker

from .debugger import Debugger

__all__ = (
    "handler", "BaseComponent", "Component", "Event", "task",
    "Worker", "Bridge", "Debugger", "Timer", "Manager", "TimeoutError",
)

# flake8: noqa
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
