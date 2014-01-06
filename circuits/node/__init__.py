# Module:   node
# Date:     ...
# Author:   ...

"""Node

Distributed and Inter-Processing support for circuits
"""

from .node import Node
from .events import remote
from .version import version as __version__

# flake8: noqa

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
