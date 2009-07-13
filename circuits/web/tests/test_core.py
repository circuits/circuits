# Module:   test_core
# Date:     16th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core Test Suite"""

import httplib
import unittest

from circuits.web import Server, Controller

from webtest import WebCase

pov = "pPeErRsSiIsStTeEnNcCeE oOfF vViIsSiIoOnN"

class Root(Controller):

    def index(self):
        return pov

    page1 = index
    page2 = index

class CoreTestCase(WebCase):

    HOST = "127.0.0.1"
    PORT = 10000

    interactive = False

    def setUp(self):
        self.server = (Server((self.HOST, self.PORT)) + Root())
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

if __name__ == "__main__":
    unittest.main()
