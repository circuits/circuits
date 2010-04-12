# Module:   utils
# Date:     11th April 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Utils

This module defines utilities used by circuits.
"""

def findroot(x):
    if x.manager == x:
        return x
    else:
        return findroot(x.manager)
