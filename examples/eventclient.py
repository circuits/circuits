#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Event Client

An example of using circuits and the event bdirge to create a simple 
server/client system. This is a really simple example and only to
demonstrate the Bridge Component.

This example demonstrates:
    * Basic Request/Response model using events.
    * Briding systems/components.

This example makes use of:
    * Component
    * Bridge
    * Manager
"""

from time import time

from circuits import Debugger
from circuits import Event, Component, Bridge, Manager

###
### Components
###

class Client(Component):

    def received(self, message):
        print message

###
### Main
###

def main():
    manager = Manager()
    debugger = Debugger()
    bridge = Bridge(8001, nodes=[("127.0.0.1", 8000)])

    debugger.IgnoreEvents = ["Read", "Write"]

    manager += bridge
    manager += debugger
    manager += Client()

    manager.start()

    sTime = time()

    while True:
        try:
            if (time() - sTime) > 5:
                manager.push(Event("Hello World"), "hello")
                sTime = time()
        except KeyboardInterrupt:
            break
    
    manager.stop()

###
### Entry Point
###

if __name__ == "__main__":
    main()
