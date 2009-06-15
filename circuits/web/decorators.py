# Module:   decorators
# Date:     2nd June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Decorators

This module implements useful decorators that can be used
to affect the behaviour of request handlers.
"""

from functools import update_wrapper

try:
    import json as _json
    HAS_JSON = 2
except ImportError:
    try:
        import simplejson as _json
        HAS_JSON = 1
    except ImportError:
        HAS_JSON = 0
        warnings.warn("No json support available.")

def json():
    def decorate(f):
        def wrapper(self, *args, **kwargs):
            return _json.dumps(f(self, *args, **kwargs))
        return update_wrapper(wrapper, f)
    return decorate

if not HAS_JSON:
    del json

def nocache():
    def decorate(f):
        def wrapper(self, *args, **kwargs):
            self.response.headers["Pragma"] = "no-cache"
            self.response.headers["Expires"] = "Sat, 1 Jan 2000 00:00:00 GMT"
            self.response.headers["Cache-Control"] = "no-cache, must-revalidate"
            return f(self, *args, **kwargs)
        return update_wrapper(wrapper, f)
    return decorate
