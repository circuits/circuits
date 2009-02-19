#!/usr/bin/env python
# Module:	main
# Date:		1st October 2008
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
	tests = ("circuits.tests.%s" % x.split(".")[0] for x in files)

	for test in tests:
		m = __import__(test, fromlist=["circuits.tests"])
		suite.addTest(m.suite())

	return suite

def main():
	unittest.main(defaultTest="suite")

if __name__ == "__main__":
	main()
