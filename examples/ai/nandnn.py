#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep, time
from random import seed, random

from circuits.lib.ann import (
        Node, Connection,
		Neuron, Output)

a = Node()
b = Node()
x = Connection()
y = Connection()
n = Neuron(type="step")
o = Output()

seed(time())

x.weight = random()
y.weight = random()
n.threshold = random()

a.link(x)
b.link(y)
x.link(n)
y.link(n)
n.link(o)

inputs = [
		(0.0, 0.0),
		(0.0, 1.0),
		(1.0, 0.0),
		(1.0, 1.0),
		]
outputs = [ 1.0, 1.0, 1.0, 0.0 ]

def train():
	done = False
	old_x_weight = x.weight
	old_y_weight = y.weight
	old_n_threshold = n.threshold
	while not done:
		for c, (i1, i2) in enumerate(inputs):
			a.fire(i1)
			b.fire(i2)
			sleep(0.05)
			t = outputs[c]
			e = t - o.output
			print "I: (%0.2f, %0.2f) O: %0.2f T: %0.2f e: %0.2f" % (
					i1, i2, o.output, t, e)

			if not o.output == t:
				I = i1 + i2 + n.threshold
				x.weight += 0.5 * e * I
				y.weight += 0.5 * e * I
				n.threshold -= 0.5 * e

		print

		if (old_x_weight == x.weight) and \
				(old_y_weight == y.weight) and \
				(old_n_threshold == n.threshold):
			done = True
		else:
			old_x_weight = x.weight
			old_y_weight = y.weight
			old_n_threshold = n.threshold

def test():
	for c, (i1, i2) in enumerate(inputs):
		a.fire(i1)
		b.fire(i2)
		sleep(0.05)
		t = outputs[c]
		e = t - o.output
		print "I: (%0.2f, %0.2f) O: %0.2f T: %0.2f e: %0.2f" % (
				i1, i2, o.output, t, e)
