"""I/O Support

This package contains various I/O Components. Provided are a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOut
and StdErr are also created by importing this package.
"""
import sys

from .events import close, open, seek, write
from .file import File
from .process import Process

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
# pylama: skip=1
