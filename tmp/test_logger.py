#!/usr/bin/python -i

from circuits import Debugger
from circuits.app.log import *

log = Logger("test.log", "test", "file", "DEBUG")
log += Debugger(logger=log)

log.start()
