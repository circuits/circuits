#!/usr/bin/env python

import math

from circuits import Component, Debugger, Event, Pool, Task


def isprime(n):
    """Returns True if n is prime and False otherwise"""
    if not isinstance(n, int):
        raise TypeError("argument passed to is_prime is not of 'int' type")
    if n < 2:
        return False
    if n == 2:
        return True
    max = int(math.ceil(math.sqrt(n)))
    i = 2
    while i <= max:
        if n % i == 0:
            return False
        i += 1
    return True


class SumPrimes(Event):
    """Sum Primes Event"""

    channel = "sum_primes"


class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self._sum = 0
        self._results = []
        self._pool = Pool()

    def check(self, value):
        if value.result and value:
            self._sum += value.event.args[1]

    def sum_primes(self, n):
        for x in xrange(n):
            e = Task(isprime, x)
            v = self.push(e, target=self._pool)
            v.onSet = "check", self
            self.results.append(v)

app = App() + Debugger()
app.push(SumPrimes(100))
app.run()
