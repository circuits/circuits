# Module:   io
# Date:     04th August 2004
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Advanced IO

This module contains various classes for advanced IO.
For instance, the Command class, used to make writing
command-style programs easier. (ie: programs that prompt for
input and accept commands and react to them)
"""

import os
import fcntl
import select

from circuits.core import Event, Component


POLL_INTERVAL = 0.00001
BUFFER_SIZE = 131072


class Read(Event): pass
class Error(Event): pass


class File(file):

    def setblocking(self, flag):
        " set/clear blocking mode"
        # get the file descriptor
        fd = self.fileno()
        # get the file's current flag settings
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        if flag:
            # clear non-blocking mode from flags
            fl = fl & ~os.O_NONBLOCK
        else:
            # set non-blocking mode from flags
            fl = fl | os.O_NONBLOCK
        # update the file's flags
        fcntl.fcntl(fd, fcntl.F_SETFL, fl)

    def write(self, str):
        try:
            return os.write(self.fileno(), str)
        except OSError, inst:
            raise IOError(inst.errno, inst.strerror, inst.filename)


class Stdin(Component):

    channel = "stdin"

    def __init__(self, channel=channel):
        super(Stdin, self).__init__(channel=channel)

        self._stdin = File("/dev/stdin", "r")
        self._stdin.setblocking(False)
        self._fds = [self._stdin]

    def __tick__(self):
        self.poll()

    def poll(self, wait=POLL_INTERVAL):
        try:
            r, w, e = select.select(self._fds, [], [], wait)
        except select.error, error:
            if error[0] == 4:
                pass
            else:
                self.push(Error(error), "error", self.channel)
                return

        if r:
            data = self._stdin.read(BUFFER_SIZE)
            if data:
                self.push(Read(data), "read", self.channel)
            else:
                self.close()
                return

    def close(self):
        self._stdin.close()
        self._fds = []
