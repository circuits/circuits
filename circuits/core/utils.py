# Module:   utils
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utils

This module defines utilities used by circuits.
"""

import sys

from imp import reload


def itercmp(x, c, subclass=True):
    if subclass and issubclass(x.__class__, c):
        yield x
    elif isinstance(x, c):
        yield x
    else:
        for component in x.components:
            if subclass and issubclass(component.__class__, c):
                yield component
            elif isinstance(component, c):
                yield component
            else:
                for component in itercmp(component, c, subclass):
                    yield component

def findcmp(x, c, subclass=True):
    components = itercmp(x, c, subclass)
    try:
        return next(components)
    except StopIteration:
        return None

def findroot(x):
    if x.manager == x:
        return x
    else:
        return findroot(x.manager)

def safeimport(name):
    modules = sys.modules.copy()
    try:
        if name in sys.modules:
            return reload(sys.modules[name])
        else:
            return __import__(name, globals(), locals(), [""])
    except:
        for name in sys.modules.copy():
            if not name in modules:
                del sys.modules[name]
