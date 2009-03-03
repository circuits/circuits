# Module:	__init__
# Date:		1st February 2009
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits Library - Drivers

circuits.lib.drivers contains drivers for other sources of events.
"""

from os import listdir as _listdir
from warnings import warn as _warn
from os.path import dirname as _dirname
from os.path import splitext as _splitext
from traceback import format_exc as _format_exc
from inspect import getmembers as _getmembers, isclass as _isclass

from circuits.core import Component as _Component

class DriverError(Exception): pass

def modules():
    for filename in _listdir(_dirname(__file__)):
        root, ext = _splitext(filename)
        if not root == "__init__" and ext == ".py":
            yield root

def load():
    drivers = {}
    for driver in modules():
        try:
            module = __import__(driver, globals(), locals(), [__package__])
            p1 = lambda x: _isclass(x) and issubclass(x, _Component)
            p2 = lambda x: x is not _Component
            predicate = lambda x: p1(x) and p2(x)
            for name, component in _getmembers(module, predicate):
                globals()[name] = component
            globals()[driver] = drivers[driver] = module
        except DriverError, e:
            _warn("Cannot load driver '%s': %s" % (driver, e))
        except Exception, e:
            print "Error loadign driver '%s': %s" % (driver, e)
            print _format_exc()
    return drivers

drivers = load()
