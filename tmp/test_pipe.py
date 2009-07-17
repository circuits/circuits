#!/usr/bin/env python

import sys
import math
import time
from time import time
import optparse

try:
    import hotshot
    import hotshot.stats
except ImportError:
    hostshot = None

try:
    import psyco
except ImportError:
    psyco = None

from circuits.net.sockets import Pipe, Write
from circuits import handler, Event, Component, Timer

from circuits import __version__ as systemVersion

USAGE = "%prog [options]"
VERSION = "%prog v" + systemVersion

###
### Functions
###

def bytes(bytes):
	if bytes >= 1024**4:
		return (round(bytes / float(1024**4), 2), "TB")
	elif bytes >= 1024**3:
		return (round(bytes / float(1024**3), 2), "GB")
	elif bytes >= 1024**2:
		return (round(bytes / float(1024**2), 2), "MB")
	elif bytes >= 1024**1:
		return (round(bytes / float(1024**1), 2), "KB")
	else:
		return bytes, "B"

def parse_options():
    """parse_options() -> opts, args

    Parse the command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-b", "--bufsize",
            action="store", type="int", default=4096, dest="bufsize",
            help="Buffer size in bytes (Default: 4096)")

    parser.add_option("-d", "--datasize",
            action="store", type="int", default=1024, dest="datasize",
            help="Data size in kilo bytes (Default: 1024)")

    parser.add_option("-i", "--input",
            action="store", type="str", default="/dev/zero", dest="input",
            help="Input file (Default: /dev/zero)")

    parser.add_option("-t", "--time",
            action="store", type="int", default=10, dest="time",
            help="Stop after specified elapsed seconds")

    parser.add_option("-p", "--profile",
            action="store_true", default=False, dest="profile",
            help="Enable execution profiling support")

    parser.add_option("-s", "--speed",
            action="store_true", default=False, dest="speed",
            help="Enable psyco (circuits on speed!)")

    parser.add_option("-q", "--quiet",
            action="store_false", default=True, dest="verbose",
            help="Suppress output")

    opts, args = parser.parse_args()

    return opts, args

###
### Events
###

class StartTest(Event): pass
class StopTest(Event): pass

###
### Components
###

class Base(Component):

    def __init__(self, opts, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

        self.opts = opts

class TestPipe(Base):

    def __init__(self, *args, **kwargs):
        super(TestPipe, self).__init__(*args, **kwargs)

        self.input = open(self.opts.input, "r")
        self.bufsize = self.opts.bufsize
        self.data = "\x00" * (1024 * self.opts.datasize)

        a, b = Pipe(bufsize=self.opts.bufsize)
        self += a
        self += b

    def starttest(self):
        self += Timer(self.opts.time, StopTest(), "stoptest")
        self.stime = time()
        self.etime = None
        self.abytes = 0
        self.bbytes = 0
        self.push(Write(self.data), target="pipe.a")

    def stoptest(self):
        self.etime = time()
        ttime = self.etime - self.stime
        tbytes = self.abytes + self.bbytes
        aspeed = "%0.2f%s/s" % bytes(self.abytes / ttime)
        bspeed = "%0.2f%s/s" % bytes(self.bbytes / ttime)
        tspeed = "%0.2f%s/s" % bytes(tbytes / ttime)
        print "A: %d bytes after %ds (%s)" % (self.abytes, ttime, aspeed)
        print "B: %d bytes after %ds (%s)" % (self.bbytes, ttime, bspeed)
        print "T: %d bytes after %ds (%s)" % (tbytes, ttime, tspeed)
        self.stop()

    @handler("read", target="pipe.a")
    def pipea_read(self, data):
        self.abytes += len(data)
        if not self.etime:
            self.push(Write(data), target="pipe.a")

    @handler("read", target="pipe.b")
    def pipeb_read(self, data):
        self.bbytes += len(data)
        if not self.etime:
            self.push(Write(data), target="pipe.b")

###
### Main
###

def main():
    opts, args = parse_options()

    if opts.speed and psyco:
        psyco.full()

    t = TestPipe(opts)

    if opts.profile:
        if hotshot:
            profiler = hotshot.Profile(".profile")
            profiler.start()

    t.push(StartTest())
    t.run()

    if opts.profile and hotshot:
        profiler.stop()
        profiler.close()

        stats = hotshot.stats.load(".profile")
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
    main()
