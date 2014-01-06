# Package:  app
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Application Components

Contains various components useful for application development and tasks
common to applications.

:copyright: CopyRight (C) 2004-2013 by James Mills
:license: MIT (See: LICENSE)
"""

from .daemon import Daemon
from .version import version as __version__

__all__ = ("Daemon",)

# flake8: noqa
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
