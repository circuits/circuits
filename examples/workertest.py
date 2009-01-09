#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

from time import sleep

from circuits.workers import Thread, Process
from circuits import listener, Event, Component, Manager

class A(Thread):

    @listener("hello")
    def onHELLO(self, message):
        self.push(Event("ok, got: %s" % message), "received")

    def run(self):
        while self.running:
            try:
                self.push(Event("Hello from %s" % self), "hello")
                sleep(1)
            except KeyboardInterrupt:
                self.stop()

class B(Process):

    @listener("hello")
    def onHELLO(self, message):
        self.push(Event("ok, got: %s" % message), "received")

    def run(self):
        while self.running:
            try:
                self.push(Event("Hello from %s" % self), "hello")
                sleep(1)
            except KeyboardInterrupt:
                self.stop()

class Master(Component):

    @listener("received")
    def onRECEIVED(self, message):
        print message

def main():
    manager = Manager()
    manager += Master()

    a = A()
    b = B()

    manager += a
    manager += b

    a.start()
    b.start()

    while True:
        try:
            b.poll()
            manager.flush()
            manager.push(Event("Hello!"), "hello")
            sleep(1)
        except KeyboardInterrupt:
            break

    a.stop()
    b.stop()

if __name__ == "__main__":
    main()
