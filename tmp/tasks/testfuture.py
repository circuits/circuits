#!/usr/bin/python -i

from time import sleep

from future import *

@expr
def prime(n):
    """Tests whether n is a prime number or not."""

    if n == 2:
        return False

    for x in xrange(2, (n - 1)):
        sleep(1)
        if not n % x:
            return False

    return True
