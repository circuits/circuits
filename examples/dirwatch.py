#!/usr/bin/env python

import sys

from circuits import Debugger
from circuits.io import Notify

driver = Notify() + Debugger()
driver.add_path(sys.argv[1])
driver.run()
