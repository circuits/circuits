#!/usr/bin/env python
"""Directory Watch Example

This example demonstrates the inotify I/O Component ``Notify`` which can
be used for real-time monitoring of file system events. The example simply
takes a path to watch as the first Command Line Argument and prints to
stdour every file system event it sees.
"""
import sys

from circuits import Component
from circuits.io import Notify


class FileWatcher(Component):

    channel = "notify"

    def opened(self, filename, path, fullpath, isdir):
        print("File {0:s} opened".format(filename))

    def closed(self, filename, path, fullpath, isdir):
        print("File {0:s} closed".format(filename))


# Configure the system
app = Notify()
FileWatcher().register(app)

# Add the path to watch
app.add_path(sys.argv[1])

# Run the system
app.run()
