#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from circuits import listener, Event, Component, Manager

class Foo(Component):

    @listener("foo")
    def onFOO(self):
        print "Foo",
        self.send(Event(), "bar")

class Bar(Component):

    @listener("bar")
    def onBAR(self):
        print "Bar!"

def main():
    manager = Manager()

    foo = Foo()
    manager += foo

    bar = Bar()
    foo += bar

    while True:
        try:
            manager.flush()
            manager.push(Event(), "foo")
            sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
