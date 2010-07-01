# Module:   utils
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utils

This module defines utilities used by circuits.
"""

def findcmp(x, c, subclass=True):
    for component in x.components:
        if subclass and issubclass(component.__class__, c):
            return component
        elif isinstance(component, c):
            return component
        else:
            return findcmp(component, c, subclass)

def findroot(x):
    if x.manager == x:
        return x
    else:
        return findroot(x.manager)
