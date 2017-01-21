"""Macro

Macro support and dispatcher
"""
import os
from inspect import getmembers, getmodule, isfunction

from creoleparser import parse_args


class Macro(object):

    def __init__(self, name, arg_string, body, isblock):
        super(Macro, self).__init__()

        self.name = name
        self.arg_string = arg_string
        self.body = body
        self.isblock = isblock


def dispatcher(name, arg_string, body, isblock, environ):
    if name in environ["macros"]:
        macro = Macro(name, arg_string, body, isblock)
        args, kwargs = parse_args(arg_string)
        try:
            return environ["macros"][name](macro, environ, *args, **kwargs)
        except Exception as e:
            return "ERROR: Error while executing macro %r (%s)" % (name, e)
    else:
        return "Macro not found!"


def loadMacros():
    path = os.path.abspath(os.path.dirname(__file__))

    def p(x):
        os.path.splitext(x)[1] == ".py"
    modules = [x for x in os.listdir(path) if p(x) and not x == "__init__.py"]

    macros = {}

    for module in modules:
        name, _ = os.path.splitext(module)

        moduleName = "%s.%s" % (__package__, name)
        m = __import__(moduleName, globals(), locals(), __package__)

        def p(x):
            isfunction(x) and getmodule(x) is m
        for name, function in getmembers(m, p):
            name = name.replace("_", "-")
            try:
                macros[name] = function
            except Exception:
                continue

    return macros
