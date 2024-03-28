"""
Utils

This module defines utilities used by circuits.
"""

import sys
from importlib import reload


def flatten(root, visited=None):
    if not visited:
        visited = set()
    yield root
    for component in root.components.copy():
        if component not in visited:
            visited.add(component)
            yield from flatten(component, visited)


def findchannel(root, channel, all=False):
    components = [x for x in flatten(root) if x.channel == channel]

    if all:
        return components

    if components:
        return components[0]
    return None


def findtype(root, component, all=False):
    components = [x for x in flatten(root) if issubclass(type(x), component)]

    if all:
        return components

    if components:
        return components[0]
    return None


findcmp = findtype


def findroot(component):
    if component.parent == component:
        return component
    return findroot(component.parent)


def safeimport(name):
    modules = sys.modules.copy()
    try:
        if name in sys.modules:
            return reload(sys.modules[name])
        return __import__(name, globals(), locals(), [''])
    except Exception:
        for name in sys.modules.copy():
            if name not in modules:
                del sys.modules[name]
