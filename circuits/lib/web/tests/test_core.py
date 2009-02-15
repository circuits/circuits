#!/usr/bin/env python
# Module:       test_core
# Date:         16th February 2009
# Author:       James Mills, prologic at shortcircuit dot net dot au

import httplib
import unittest

from circuits.workers import Thread
from circuits.web import Server, Controller

from webtest import WebCase

pov = "pPeErRsSiIsStTeEnNcCeE oOfF vViIsSiIoOnN"

class Root(Controller):

    def index(self):
        return pov

    page1 = index
    page2 = index

class TestServer(Thread):

    def run(self):
        server = Server(8000)
        server += Root()

        while self.isAlive():
            try:
                server.flush()
                server.poll()
            except Exception, error:
                print "ERROR: %s" % error

class Test(WebCase):

    def setUp(self):
        self.server = TestServer()
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_HTTP11(self):
        self.PROTOCOL = "HTTP/1.1"

        self.persistent = True

        # Make the first request and assert there's no "Connection: close".
        self.getPage("/")
        self.assertStatus("200 OK")
        self.assertBody(pov)
        self.assertNoHeader("Connection")

        # Make another request on the same connection.
        self.getPage("/page1")
        self.assertStatus("200 OK")
        self.assertBody(pov)
        self.assertNoHeader("Connection")

        # Test client-side close.
        self.getPage("/page2", headers=[("Connection", "close")])
        self.assertStatus("200 OK")
        self.assertBody(pov)
        self.assertHeader("Connection", "close")

        # Make another request on the same connection, which should error.
        self.assertRaises(httplib.NotConnected, self.getPage, "/")

def suite():
    return unittest.makeSuite(EventTestCase, "test")

if __name__ == "__main__":
    unittest.main()
