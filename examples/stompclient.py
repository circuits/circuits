#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example usage for StompClient component

Requires a STOMP server to connect to.

"""

import logging
import ssl
from circuits import Component, Timer, Event
from circuits.core.handlers import handler
from circuits.protocols.stomp.client import StompClient, ACK_AUTO
from circuits.protocols.stomp.events import *

LOG = logging.getLogger(__name__)

class QueueHandler(Component):
    def __init__(self, queue, host=None, *args, **kwargs):
        super(QueueHandler, self).__init__(*args, **kwargs)
        self.queue = queue
        self.host=host

    def registered(self, event, component, parent):
        if component.parent is self:
            self.fire(Event.create("Reconnect"))

    def Connected(self):
        """Client has connected to the STOMP server"""
        LOG.info("STOMP connected.")
        # Let's subscribe to the message destination
        self.fire(Subscribe(self.queue, ack=ACK_AUTO))

    def Subscribe_success(self, event, *args, **kwargs):
        """ Subscribed to message destination """
        # Let's fire off some messages
        self.fire(Send(headers = None,
                       body="Hello World",
                       destination=self.queue))
        self.fire(Send(headers = None,
                       body="Hello Again World",
                       destination=self.queue))

    def HeartbeatTimeout(self):
        """Heartbeat timed out from the STOMP server"""
        LOG.error("STOMP heartbeat timeout!")
        # Set a timer to automatically reconnect
        Timer(10, Event.create("Reconnect")).register(self)

    def OnStompError(self, headers, message, error):
        """STOMP produced an error."""
        LOG.error('STOMP listener: Error:\n%s', message or error)

    def Message(self, event, headers, message):
        """STOMP produced a message."""
        LOG.info("Message Received: %s", message)

    def Disconnected(self, event, *args, **kwargs):
        # Wait a while then try to reconnect
        LOG.info("We got disconnected, reconnect")
        Timer(10, Event.create("Reconnect")).register(self)

    def Reconnect(self):
        """Try (re)connect to the STOMP server"""
        LOG.info("STOMP attempting to connect")
        self.fire(Connect(host=self.host))



def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    # Configure and run
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # You can create an STOMP server to test for free at https://www.cloudamqp.com/
    uri = "orangutan.rmq.cloudamqp.com"
    port = 61614
    login = "cjferxig"
    passcode="5fyrCArVx4RY6mAwUiM7Mbd_FEnwYwUU"
    host = "cjferxig"
    queue = "test1"

    s = StompClient(uri, port,
                    username=login,
                    password=passcode,
                    heartbeats=(10000, 10000),
                    ssl_context=context)

    qr = QueueHandler(queue, host=host)
    s.register(qr)

    qr.run()

if __name__ == "__main__":
    main()
