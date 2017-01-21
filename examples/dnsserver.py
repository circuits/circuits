#!/usr/bin/env python
"""DNS Server Example

A simple little DNS Server example using
`dnslib <https://pypi.python.org/pypi/dnslib>`_
to handle the DNS protocol parsing and packet
construction (*a really nice library btw with
great integration into circuits*).

Answers ``A 127.0.0.1`` for any query of any type!

To run this example::

    pip install dnslib
    ./dnsserver.py

Usage (*using dig*)::

    dig @localhost -p 1053 test.com

"""
from __future__ import print_function

import sys

from dnslib import QTYPE, RR, A, DNSHeader, DNSRecord

from circuits import Component, Debugger, Event
from circuits.net.events import write
from circuits.net.sockets import UDPServer


class query(Event):

    """query Event"""


class DNS(Component):

    """DNS Protocol Handling"""

    def read(self, peer, data):
        self.fire(query(peer, DNSRecord.parse(data)))


class Dummy(Component):

    """A Dummy DNS Handler

    This just returns an A record response
    of 127.0.0.1 for any query of any type!
    """

    def query(self, peer, request):
        id = request.header.id
        qname = request.q.qname

        print(
            "DNS Request for qname({0:s})".format(str(qname)),
            file=sys.stderr
        )

        reply = DNSRecord(
            DNSHeader(id=id, qr=1, aa=1, ra=1),
            q=request.q
        )

        # Add A Record
        reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1")))

        # Send To Client
        self.fire(write(peer, reply.pack()))


class DNSServer(Component):

    """DNS Server

    This ties everything together in a nice
    configurable way with protocol, transport
    and dummy handler as well as optional debugger.
    """

    def init(self, bind=None, verbose=False):
        self.bind = bind or ("0.0.0.0", 53)

        if verbose:
            Debugger().register(self)

        self.transport = UDPServer(self.bind).register(self)
        self.protocol = DNS().register(self)
        self.dummy = Dummy().register(self)

    def started(self, manager):
        print("DNS Server Started!", file=sys.stderr)

    def ready(self, server, bind):
        print("Ready! Listening on {0:s}:{1:d}".format(*bind), file=sys.stderr)


DNSServer(("0.0.0.0", 1053), verbose=True).run()
