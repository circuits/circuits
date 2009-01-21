#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Tool) Bench Marking Tool

THis tool does some simple benchmaking of the circuits library.
"""

import sys
import math
import time
import hotshot
import optparse
import hotshot.stats

try:
	import psyco
except ImportError:
	psyco = None

from circuits import listener, Event, Component, Bridge, Manager
from circuits import __version__ as systemVersion

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

	opts, args = parser.parse_args()

	try:
		opts.events = int(opts.events)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[1][0], ERRORS[1][1])

	try:
		opts.time = int(opts.time)
	except Exception, e:
		print str(e)
		parser.exit(ERRORS[2][0], ERRORS[2][1])

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

class Sender(Component):

	concurrency = 1

	@listener("received")
	def onRECEIVED(self, message=""):
		self.push(Hello("hello"), "hello", self.channel)

class Receiver(Component):

	@listener("helo")
	def onHELO(self, address, port):
		self.push(Hello("hello"), "hello", self.channel)

	@listener("hello")
	def onHELLO(self, message=""):
		self.push(Received(message), "received", self.channel)

class SpeedTest(Component):

	@listener("hello")
	def onHELLO(self, message):
		self.push(Hello(message), "hello", self.channel)

class LatencyTest(Component):

	t = None

	@listener("received")
	def onRECEIVED(self, message=""):
		print "Latency: %0.2f ms" % ((time.time() - self.t) * 1000)
		time.sleep(1)
		self.push(Hello("hello"), "hello", self.channel)

	@listener("hello")
	def onHELLO(self, message=""):
		self.t = time.time()
		self.push(Received(message), "received", self.channel)
	
class State(Component):

	done = False

	@listener("stop")
	def onSTOP(self):
		self.push(Term(), "term")

	@listener("term")
	def onTERM(self):
		self.done = True

class Monitor(Component):

	sTime = sys.maxint
	events = 0
	state = 0

	@listener("helo")
	def onHELO(self, *args, **kwargs):
		print "Resetting sTime"
		self.sTime = time.time()

	@listener(type="filter")
	def onEVENTS(self, *args, **kwargs):
		self.events += 1

###
### Main
###

def main():
	opts, args = parse_options()

	if opts.speed and psyco:
		psyco.full()

	manager = Manager()

	monitor = Monitor()
	manager += monitor

	state = State()
	manager += state

	if opts.debug:
		debugger.enable()
		manager += debugger

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

		bridge = Bridge(port, address=address, nodes=nodes)
		manager += bridge
	else:
		bridge = None

	if opts.mode.lower() == "speed":
		print "Setting up Speed Test..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				manager += SpeedTest(channel=c)
		else:
			manager += SpeedTest()
		monitor.sTime = time.time()
	elif opts.mode.lower() == "latency":
		print "Setting up Latency Test..."
		manager += LatencyTest()
		monitor.sTime = time.time()
	elif opts.listen:
		print "Setting up Receiver..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				manager += Receiver(channel=c)
		else:
			manager += Receiver()
	elif args:
		print "Setting up Sender..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				manager += Sender(channel=c)
		else:
			manager += Sender()
	else:
		print "Setting up Sender..."
		print "Setting up Receiver..."
		if opts.concurrency > 1:
			for c in xrange(int(opts.concurrency)):
				manager += Sender(channel=c)
				manager += Receiver(channel=c)
		else:
			manager += Sender()
			manager += Receiver()
		monitor.sTime = time.time()

	if opts.profile:
		profiler = hotshot.Profile("bench.prof")
		profiler.start()

	if opts.concurrency > 1:
		for c in xrange(int(opts.concurrency)):
			manager.push(Hello("hello"), "hello", c)
	else:
		manager.push(Hello("hello"), "hello")

	while not state.done:
		try:
			manager.flush()
			if bridge:
				bridge.poll()

			for i in xrange(opts.fill):
				manager.push(Foo(), "foo")

			if opts.events > 0 and monitor.events > opts.events:
				manager.send(Stop(), "stop")
			if opts.time > 0 and (time.time() - monitor.sTime) > opts.time:
				manager.send(Stop(), "stop")

		except KeyboardInterrupt:
			manager.send(Stop(), "stop")

	print

	eTime = time.time()

	tTime = eTime - monitor.sTime

	print "Total Events: %d (%d/s after %0.2fs)" % (
			monitor.events, int(math.ceil(float(monitor.events) / tTime)), tTime)

	if opts.profile:
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
