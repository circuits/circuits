"""
Utils macros

Utility macros
"""

from inspect import getdoc


def macros(macro, environ, *args, **kwargs):
    """Return a list of available macros"""
    macros = environ['macros'].items()
    s = '\n'.join([f'== {k} ==\n{getdoc(v)}\n' for k, v in macros])

    return environ['parser'].generate(s, environ=environ)
