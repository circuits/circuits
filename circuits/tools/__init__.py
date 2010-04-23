# Module:   __init__
# Date:     8th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""

from hashlib import md5

try:
    import pydot
    HAS_PYDOT = True
except ImportError:
    HAS_PYDOT = False

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
    if x.manager == x:
        return x
    else:
        return findroot(x.manager)

def kill(x):
    for c in x.components.copy():
        kill(c)
    if x.manager != x:
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
        return "%s-%s" % (c.name, md5(str(hash(c))).hexdigest()[-4:])

    if HAS_PYDOT:
        graph_edges = []
        for (u, v) in edges(x):
            graph_edges.append(("\"%s\"" % getname(u), "\"%s\"" % getname(v)))

        g = pydot.graph_from_edges(graph_edges, directed=True)
        g.write("%s.dot" % (name or x.name))
        g.write("%s.png" % (name or x.name), format="png")

    def printer(d, x):
        return "%s* %s" % (" " * d, x)

    return "\n".join(walk(x, printer))
    
def reprhandler(c, h):
    """Display a nicely formatted Event Handler, h from Component c.

    :param c: A Component that contains Event Handler h
    :type c: Manager or Manager subclass

    :param x: An Event Handler
    :type  x: function or method

    @return: A nicely formatted representation of the Event Handler, x
    @rtype:  str
    """

    attrs = c._handlerattrs[h]

    format = "<%s on %s {target=%s, priority=%0.1f}>"
    channels = repr(attrs["channels"])
    f = "filter" if attrs["filter"] else "listener"
    t = repr(attrs["target"])
    p = attrs["priority"]
    return format % (f, channels, t, p)

def inspect(x):
    """Display an inspection report of the Component or Manager x

    :param x: A Component or Manager to graph
    :type  x: Component or Manager

    @return: A detailed inspection report of x
    @rtype:  str
    """

    s = []
    write = s.append

    write(" Registered Components: %d\n" % len(x.components))
    for component in x.components:
        write("  %s\n" % component)
    write("\n")

    write(" Tick Functions: %d\n" % len(x._ticks))
    for tick in x._ticks:
        write("  %s\n" % tick)
    write("\n")

    write(" Channels and Event Handlers: %d\n" % len(x.channels))
    for (t, c) in x.channels:
        write("  %s:%s; %d\n" % (t, c, len(x.channels[(t, c)])))
        for handler in x.channels[(t, c)]:
            write("   %s\n" % reprhandler(x, handler))

    return "".join(s)
