#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep, time
from random import seed, random

from circuits.lib.ann import (
        Node, Connection,
		Neuron, Output)

def debug(n):
	print n.output

a = Node()
b = Node()
s1 = Connection()
s2 = Connection()
s3 = Connection()
s4 = Connection()
s5 = Connection()
s6 = Connection()
n1 = Neuron(type="step")
n2 = Neuron(type="step")
n3 = Neuron(type="step")
o = Output()
d1 = Output(f=debug)
d2 = Output(f=debug)

seed(time())

s1.weight = random()
s2.weight = random()
s3.weight = random()
s4.weight = random()
s5.weight = random()
s6.weight = random()
n1.threshold = random()
n2.threshold = random()
n3.threshold = random()

a.link(s1)
a.link(s2)
b.link(s3)
b.link(s4)

s1.link(n1)
s2.link(n2)
s3.link(n1)
s4.link(n2)

n1.link(s5)
n2.link(s6)
n1.link(d1)
n2.link(d2)

s5.link(n3)
s6.link(n3)

n3.link(o)

inputs = [
		(0.0, 0.0),
		(0.0, 1.0),
		(1.0, 0.0),
		(1.0, 1.0),
		]
outputs = [ 0.0, 1.0, 1.0, 0.0 ]

def train():
	for c, (i1, i2) in enumerate(inputs):
		a.fire(i1)
		b.fire(i2)
		sleep(0.1)
		t = outputs[c]
		e = t - o.output
		print "I: (%0.2f, %0.2f) O: %0.2f T: %0.2f e: %0.2f" % (
				i1, i2, o.output, t, e)

		if not o.output == t:
			I = i1 + i2 + n1.threshold + \
					n2.threshold + n3.threshold
			s1.weight += 0.5 * e * I
			s2.weight += 0.5 * e * I
			s3.weight += 0.5 * e * I
			s4.weight += 0.5 * e * I
			s5.weight += 0.5 * e * I
			s6.weight += 0.5 * e * I
			n1.threshold -= 0.5 * e
			n2.threshold -= 0.5 * e
			n3.threshold -= 0.5 * e

def test():
	for c, (i1, i2) in enumerate(inputs):
		a.fire(i1)
		b.fire(i2)
		sleep(0.1)
		t = outputs[c]
		e = t - o.output
		print "I: (%0.2f, %0.2f) O: %0.2f T: %0.2f e: %0.2f" % (
				i1, i2, o.output, t, e)
