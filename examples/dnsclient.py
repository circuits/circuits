#!/usr/bin/env python
"""DNS Client Example

A simple little DNS Client example using
`dnslib <https://pypi.python.org/pypi/dnslib>`_
to handle the DNS protocol parsing and packet
deconstruction (*a really nice library btw with
great integration into circuits*).

Specify the server, port, and query as arguments
to perform a lookup against a server using UDP.

To run this example::

    pip install dnslib
    ./dnsclient.py 8.8.8.8 53 google.com
"""
from __future__ import print_function

import sys

from dnslib import DNSQuestion, DNSRecord

from circuits import Component, Debugger, Event
from circuits.net.events import write
from circuits.net.sockets import UDPClient


class reply(Event):

    """reply Event"""


class DNS(Component):

    """DNS Protocol Handling"""

    def read(self, peer, data):
        self.fire(reply(peer, DNSRecord.parse(data)))


class Dummy(Component):

    """A Dummy DNS Handler

    This just parses the reply packet and
    prints any RR records it finds.
    """

    def reply(self, peer, response):
        id = response.header.id
        qname = response.q.qname

        print(
            "DNS Response from {0:s}:{1:d} id={2:d} qname={3:s}".format(
                peer[0], peer[1], id, str(qname)
            ),
            file=sys.stderr
        )

        for rr in response.rr:
            print(" {0:s}".format(str(rr)))

        raise SystemExit(0)


class DNSClient(Component):

    """DNS Client

    This ties everything together in a nice
    configurable way with protocol, transport,
    and dummy handler as well as optional debugger.
    """

    def init(self, server, port, query, verbose=False):
        self.server = server
        self.port = int(port)
        self.query = query

        if verbose:
            Debugger().register(self)

        self.transport = UDPClient(0).register(self)
        self.protocol = DNS().register(self)
        self.dummy = Dummy().register(self)

    def started(self, manager):
        print("DNS Client Started!", file=sys.stderr)

    def ready(self, client, bind):
        print("Ready! Bound to {0:s}:{1:d}".format(*bind), file=sys.stderr)

        request = DNSRecord(q=DNSQuestion(self.query))
        self.fire(write((self.server, self.port), request.pack()))


DNSClient(*sys.argv[1:], verbose=True).run()
