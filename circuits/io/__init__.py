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
from .events import Close, Seek, Write

try:
    from .notify import Notify
except:
    pass

try:
    from .serial import Serial
except:
    pass

try:
    stdin = File(fd=sys.stdin, mode="r", channel="stdin")
    stdout = File(fd=sys.stdout, mode="w", channel="stdout")
    stderr = File(fd=sys.stderr, mode="w", channel="stderr")
except:
    pass
