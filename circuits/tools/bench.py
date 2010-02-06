#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Tool) Bench Marking Tool

THis tool does some simple benchmaking of the circuits library.
"""

import sys
import math
import time
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

from circuits import __version__ as systemVersion
from circuits import handler, Event, Component, Bridge, Manager, Debugger

USAGE = "%prog [options]"
VERSION = "%prog v" + systemVersion

ERRORS = [
        (0, "Cannot listen and connect at the same time!"),
        (1, "Invalid events spcified. Must be an integer."),
        (2, "Invalid time spcified. Must be an integer."),
        (3, "Invalid nthreads spcified. Must be an integer."),
        ]

###
### Functions
###

def duration(seconds):
    days = int(seconds / 60 / 60 / 24)
    seconds = (seconds) % (60 * 60 * 24)
    hours = int((seconds / 60 / 60))
    seconds = (seconds) % (60 * 60)
    mins = int((seconds / 60))
    seconds = int((seconds) % (60))
    return (days, hours, mins, seconds)

def parse_options():
    """parse_options() -> opts, args

    Parse the command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-l", "--listen",
            action="store_true", default=False, dest="listen",
            help="Listen on 0.0.0.0:8000 (UDP) to test remote events")

    parser.add_option("-w", "--wait",
            action="store_true", default=False, dest="wait",
            help="Wait for remove ndoes to conenct")

    parser.add_option("-b", "--bind",
            action="store", type="string", default="0.0.0.0", dest="bind",
            help="Bind to address:[port] (UDP) to test remote events")

    parser.add_option("-c", "--concurrency",
            action="store", type="int", default=1, dest="concurrency",
            help="Set concurrency level")

    parser.add_option("-t", "--time",
            action="store", type="int", default=0, dest="time",
            help="Stop after specified elapsed seconds")

    parser.add_option("-e", "--events",
            action="store", type="int", default=0, dest="events",
            help="Stop after specified number of events")

    parser.add_option("-p", "--profile",
            action="store_true", default=False, dest="profile",
            help="Enable execution profiling support")

    parser.add_option("-m", "--mode",
            action="store", type="choice", default="speed", dest="mode",
            choices=["sync", "speed", "latency"],
            help="Operation mode")

    parser.add_option("-f", "--fill",
            action="store", type="int", default=0, dest="fill",
            help="No. of dummy events to fill queue with")

    parser.add_option("-d", "--debug",
            action="store_true", default=False, dest="debug",
            help="Enable debug mode")

    parser.add_option("-s", "--speed",
            action="store_true", default=False, dest="speed",
            help="Enable psyco (circuits on speed!)")

    parser.add_option("-o", "--output",
            action="store", default=None, dest="output",
            help="Specify output format")

    parser.add_option("-q", "--quiet",
            action="store_false", default=True, dest="verbose",
            help="Suppress output")

    opts, args = parser.parse_args()

    if opts.listen and args:
        parser.exit(ERRORS[0][0], ERRORS[0][1])

    return opts, args

###
### Events
###

class Stop(Event): pass
class Term(Event): pass
class Hello(Event): pass
class Received(Event): pass
class Foo(Event): pass

###
### Components
###

class Base(Component):

    def __init__(self, opts, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

        self.opts = opts

class Sender(Base):

    concurrency = 1

    def received(self, message=""):
        self.push(Hello("hello"))

class Receiver(Base):

    def helo(self, address, port):
        self.push(Hello("hello"))

    def hello(self, message=""):
        self.push(Received(message))

class SpeedTest(Base):

    def hello(self, message):
        self.push(Hello(message))

class LatencyTest(Base):

    t = None

    def received(self, message=""):
        print "Latency: %0.3f us" % ((time.time() - self.t) * 1e6)
        time.sleep(1)
        self.push(Hello("hello"))

    def hello(self, message=""):
        self.t = time.time()
        self.push(Received(message))
    
class State(Base):

    done = False

    def stop(self):
        self.push(Term())

    def term(self):
        self.done = True

class Monitor(Base):

    sTime = sys.maxint
    events = 0
    state = 0

    def helo(self, *args, **kwargs):
        if self.opts.verbose:
            print "Resetting sTime"
        self.sTime = time.time()

    @handler(filter=True)
    def event(self, *args, **kwargs):
        self.events += 1

###
### Main
###

def main():
    opts, args = parse_options()

    if opts.speed and psyco:
        psyco.full()

    manager = Manager()

    monitor = Monitor(opts)
    manager += monitor

    state = State(opts)
    manager += state

    if opts.debug:
        manager += Debugger()

    if opts.listen or args:
        nodes = []
        if args:
            for node in args:
                if ":" in node:
                    host, port = node.split(":")
                    port = int(port)
                else:
                    host = node
                    port = 8000
                nodes.append((host, port))

        if opts.bind is not None:
            if ":" in opts.bind:
                address, port = opts.bind.split(":")
                port = int(port)
            else:
                address, port = opts.bind, 8000

        bridge = Bridge(bind=(address, port), nodes=nodes)
        manager += bridge

    if opts.mode.lower() == "speed":
        if opts.verbose:
            print "Setting up Speed Test..."
        if opts.concurrency > 1:
            for c in xrange(int(opts.concurrency)):
                manager += SpeedTest(opts, channel=c)
        else:
            manager += SpeedTest(opts)
        monitor.sTime = time.time()
    elif opts.mode.lower() == "latency":
        if opts.verbose:
            print "Setting up Latency Test..."
        manager += LatencyTest(opts)
        monitor.sTime = time.time()
    elif opts.listen:
        if opts.verbose:
            print "Setting up Receiver..."
        if opts.concurrency > 1:
            for c in xrange(int(opts.concurrency)):
                manager += Receiver(opts, channel=c)
        else:
            manager += Receiver(opts)
    elif args:
        if opts.verbose:
            print "Setting up Sender..."
        if opts.concurrency > 1:
            for c in xrange(int(opts.concurrency)):
                manager += Sender(opts, channel=c)
        else:
            manager += Sender(opts)
    else:
        if opts.verbose:
            print "Setting up Sender..."
            print "Setting up Receiver..."
        if opts.concurrency > 1:
            for c in xrange(int(opts.concurrency)):
                manager += Sender(channel=c)
                manager += Receiver(opts, channel=c)
        else:
            manager += Sender(opts)
            manager += Receiver(opts)
        monitor.sTime = time.time()

    if opts.profile:
        if hotshot:
            profiler = hotshot.Profile("bench.prof")
            profiler.start()

    if not opts.wait:
        if opts.concurrency > 1:
            for c in xrange(int(opts.concurrency)):
                manager.push(Hello("hello"), "hello", c)
        else:
            manager.push(Hello("hello"))

    while not state.done:
        try:
            manager.flush()

            for i in xrange(opts.fill):
                manager.push(Foo())

            if opts.events > 0 and monitor.events > opts.events:
                manager.push(Stop())
            if opts.time > 0 and (time.time() - monitor.sTime) > opts.time:
                manager.push(Stop())

        except KeyboardInterrupt:
            manager.push(Stop())

    if opts.verbose:
        print

    eTime = time.time()

    tTime = eTime - monitor.sTime

    events = monitor.events
    speed = int(math.ceil(float(monitor.events) / tTime))

    if opts.output:
        print opts.output % (events, speed, tTime)
    else:
        print "Total Events: %d (%d/s after %0.2fs)" % (events, speed, tTime)

    if opts.profile and hotshot:
        profiler.stop()
        profiler.close()

        stats = hotshot.stats.load("bench.prof")
        stats.strip_dirs()
        stats.sort_stats("time", "calls")
        stats.print_stats(20)

###
### Entry Point
###

if __name__ == "__main__":
    main()
