#!/usr/bin/env python
# Module:	main
# Date:		16th February 2009
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Main

Main Entry Point to run all the tests in the test suite.
"""

import re
import os.path
import unittest

def suite():
	suite = unittest.TestSuite()

	p = re.compile("^test_[a-z]+\.py$")
	files = (x for x in os.listdir(os.path.dirname(__file__)) if p.match(x))
	tests = ("circuits.lib.web.tests.%s" % x.split(".")[0] for x in files)

	for test in tests:
		m = __import__(test, fromlist=["circuits.lib.web.tests"])
		suite.addTest(m.suite())

	return suite

def main():
	unittest.main(defaultTest="suite")

if __name__ == "__main__":
	main()
