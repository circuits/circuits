# Module:   utils
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utils

This module defines utilities used by circuits.
"""

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
        return components.next()
    except StopIteration:
        return None

def findroot(x):
    if x.manager == x:
        return x
    else:
        return findroot(x.manager)
