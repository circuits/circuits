# Package:  net
# Date:     7th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Networking Components

This package contains components that implement network sockets and
protocols for implementing client and server network applications.

:copyright: CopyRight (C) 2004-2013 by James Mills
:license: MIT (See: LICENSE)
"""

from .version import version as __version__

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
