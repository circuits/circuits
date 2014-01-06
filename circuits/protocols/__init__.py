# Package:  protocols
# Date:     13th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Networking Protocols

This package contains components that implement various networking protocols.
"""

from .irc import IRC
from .line import Line
from .version import version as __version__

# flake8: noqa

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
