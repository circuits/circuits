# Module:   __init__
# Date:     8th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""

from hashlib import md5
from warnings import warn


class Unknown(object):
    """Unknown Dummy Component"""


def tryimport(modules, message=None):
    if isinstance(modules, str):
        modules = (modules,)
    for module in modules:
        try:
            return __import__(module, globals(), locals())
        except ImportError:
            pass
    if message:
        warn(message)


def walk(x, f, d=0, v=None):
    if not v:
        v = set()
    yield f(d, x)
    for c in x.components.copy():
        if c not in v:
            v.add(c)
            for r in walk(c, f, d + 1, v):
                yield r


def edges(x, e=None, v=None):
    if not e:
        e = set()
    if not v:
        v = []
    for c in x.components.copy():
        e.add((x, c))
        edges(c, e, v)
    return e


def findroot(x):
    if x.parent == x:
        return x
    else:
        return findroot(x.parent)


def kill(x):
    for c in x.components.copy():
        kill(c)
    if x.parent is not x:
        x.unregister()


def graph(x, name=None):
    """Display a directed graph of the Component structure of x

    :param x: A Component or Manager to graph
    :type  x: Component or Manager

    :param name: A name for the graph (defaults to x's name)
    :type  name: str

    @return: A directed graph representing x's Component sturcture.
    @rtype:  str
    """

    def getname(c):
        s = "%d" % id(c)
        h = md5(s.encode("utf-8")).hexdigest()[-4:]
        return "%s-%s" % (c.name, h)

    pydot = tryimport("pydot")
    if pydot is not None:
        graph_edges = []
        for (u, v) in edges(x):
            graph_edges.append(("\"%s\"" % getname(u), "\"%s\"" % getname(v)))

        g = pydot.graph_from_edges(graph_edges, directed=True)
        g.write("%s.dot" % (name or x.name))
        try:
            g.write("%s.png" % (name or x.name), format="png")
        except pydot.InvocationException:
            pass

    def printer(d, x):
        return "%s* %s" % (" " * d, x)

    return "\n".join(walk(x, printer))


def reprhandler(handler):
    format = "<%s[%s.%s] (%s.%s)>"

    channel = handler.channel or "*"
    names = ".".join(handler.names)
    type = "filter" if handler.filter else "listener"

    instance = getattr(handler, "im_self",
            getattr(handler, "__self__", Unknown())).__class__.__name__
    method = handler.__name__

    return format % (type, channel, names, instance, method)


def inspect(x):
    """Display an inspection report of the Component or Manager x

    :param x: A Component or Manager to graph
    :type  x: Component or Manager

    @return: A detailed inspection report of x
    @rtype:  str
    """

    s = []
    write = s.append

    write(" Components: %d\n" % len(x.components))
    for component in x.components:
        write("  %s\n" % component)
    write("\n")

    ticks = x.getTicks()
    write(" Tick Functions: %d\n" % len(ticks))
    for tick in ticks:
        write("  %s\n" % tick)
    write("\n")

    write(" Event Handlers: %d\n" % len(x._handlers.values()))
    for event, handlers in x._handlers.items():
        write("  %s; %d\n" % (event, len(x._handlers[event])))
        for handler in x._handlers[event]:
            write("   %s\n" % reprhandler(handler))

    return "".join(s)
