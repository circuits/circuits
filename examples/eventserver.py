#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Event Server

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

from circuits import Event, Component, Bridge, Manager, Debugger

###
### Components
###

class Server(Component):

    def hello(self, message):
        self.push(Event("Received: %s" % message), "received")

###
### Main
###

def main():
    manager = Manager()
    debugger = Debugger()
    bridge = Bridge(8000)

    debugger.IgnoreEvents = ["Read", "Write"]

    manager += bridge
    manager += debugger
    manager += Server()

    manager.run()

###
### Entry Point
###

if __name__ == "__main__":
    main()
