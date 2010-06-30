"""Utils macros

Utility macros
"""

def macros(macro, environ, *args, **kwargs):
    """Return a list of available macros"""

    s = "\n".join(["* %s" % k for k in environ["macros"].keys()])

    return environ["parser"].generate(s, environ=environ)
