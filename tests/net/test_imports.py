#!/usr/bin/env python

from circuits.core.components import BaseComponent

def test():
    try:
        from circuits.net.pollers import BasePoller
        assert issubclass(BasePoller, BaseComponent)
    except ImportError:
        assert False
