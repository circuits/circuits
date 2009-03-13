# Module:   io
# Date:     4th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""I/O Components

This package contains various I/O Components. Provided are a a generic File
Component, StdIn, StdOut and StdErr components. Instances of StdIn, StdOUt
and StdErr are also created by importing this package.
"""

from file import File

class StdIn(File):

    channel = "stdin"

    def __init__(self, channel=channel):
        super(StdIn, self).__init__("/dev/stdin", "r", channel=channel)

class StdOut(File):

    channel = "stdout"

    def __init__(self, channel=channel):
        super(StdOut, self).__init__("/dev/stdout", "w", channel=channel)

class StdErr(File):

    channel = "stderr"

    def __init__(self, channel=channel):
        super(StdErr, self).__init__("/dev/stderr", "w", channel=channel)

stdin = StdIn()
stdout = StdOut()
stderr = StdErr()
