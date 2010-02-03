# Module:   line
# Date:     04th February 2010
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Line Protocol

This module implements the basic Line protocol.

This module can be used in both server and client implementations.
"""

import re

from circuits.core import handler, Event, BaseComponent

LINESEP = re.compile("\r?\n")

def splitLines(s, buffer):
    """splitLines(s, buffer) -> lines, buffer

    Append s to buffer and find any new lines of text in the
    string splitting at the standard IRC delimiter CRLF. Any
    new lines found, return them as a list and the remaining
    buffer for further processing.
    """

    lines = LINESEP.split(buffer + s)
    return lines[:-1], lines[-1]

class Line(Event):
    """Line Event

    This Event is sent for each line processed by the LP Protocol Component.

    @param line: a single line of data
    @type  line: str
    """

    def __init__(self, line):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Line, self).__init__(line)


class LP(BaseComponent):
    """Line Protocol

    Implements the Line Protocol.

    Incoming data is split into lines with a splitter function. For each
    line of data processed a Line Event is created. Any unfinished lines
    are appended into an internal buffer.

    @note: This Component must be used in conjunction with a Component that
           exposes Read events on a "read" Channel.
    """

    channel = "*"

    def __init__(self, splitter=splitLines, channel=channel):
        super(LP, self).__init__(channel=channel)

        self.splitter = splitter
        self.buffer = ""

    @handler("read")
    def read(self, data):
        lines, self.buffer = self.splitter(data, self.buffer)
        for line in lines:
            if self.children:
                self.send(Line(line))
            else:
                self.push(Line(line))
