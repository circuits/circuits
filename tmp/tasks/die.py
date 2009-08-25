#!/usr/bin/python

from fun import *

@task
def foo():
    while 1:
        print "foo"
        sleep(0.5)

@task
def bar():
    sleep(3.0)
    scheduler.unswitch()

scheduler.start()

foo()
bar()

#scheduler.switch()
print 'finished'
