#!/usr/bin/env python

"""Test Service

...
"""

from optparse import OptionParser

from circuits import Component

from service import install_service, Service

__version__ = "0.0.1"

USAGE = "%prog [<options>] <command>"
VERSION = "%prog v" + __version__

class App(Component):

    def started(self, component, mode):
        pass

class TestService(Service):

    app = App()

def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    #parser.add_option("-x", "--xxx",
    #       action="store", type="string",
    #       default=None, dest="x",
    #       help="xxx")

    opts, args = parser.parse_args()

    if not args:
        parser.print_usage()
        raise SystemExit, -1

    return opts, args

def main():
    opts, args = parse_options()

    if args and args[0] == "install":
        install_service(TestService)

if __name__ == "__main__":
    main()
