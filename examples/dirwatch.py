#!/usr/bin/env python

"""Directory Watch Example

This example demonstrates the inotify I/O Component ``Notify`` which can
be used for real-time monitoring of file system events. The example simply
takes a path to watch as the first Command Line Argument and prints to
stdour every file system event it sees.
"""

import sys

from circuits import Debugger
from circuits.io import Notify

# Configure the system
app = Notify()
Debugger().register(app)

# Add the path to watch
app.add_path(sys.argv[1])

# Run the system
app.run()
