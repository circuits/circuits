# Module:   io
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Support

This package contains various I/O Components. Provided are a a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOUt
and StdErr are also created by importing this package.
"""

import sys

from .file import File
from .process import Process
from .events import close, open, seek, write

from .version import version as __version__

try:
    from .notify import Notify
except:
    pass

try:
    from .serial import Serial
except:
    pass

try:
    stdin = File(sys.stdin, channel="stdin")
    stdout = File(sys.stdout, channel="stdout")
    stderr = File(sys.stderr, channel="stderr")
except:
    pass

# flake8: noqa
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
