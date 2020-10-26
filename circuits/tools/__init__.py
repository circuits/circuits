"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""
import inspect as _inspect
from functools import wraps
from warnings import warn, warn_explicit

from circuits.six import _func_code


def tryimport(modules, obj=None, message=None):
    modules = (modules,) if isinstance(modules, str) else modules

    for module in modules:
        try:
            m = __import__(module, globals(), locals())
            return getattr(m, obj) if obj is not None else m
        except Exception:
            pass

    if message is not None:
        warn(message)


def getargspec(func):
    getargs = _inspect.getfullargspec if hasattr(_inspect, 'getfullargspec') else _inspect.getargspec
    return getargs(func)[:4]


def walk(x, f, d=0, v=None):
    if not v:
        v = set()
    yield f(d, x)
    for c in x.components.copy():
        if c not in v:
            v.add(c)
            for r in walk(c, f, d + 1, v):
                yield r


def edges(x, e=None, v=None, d=0):
    if not e:
        e = set()
    if not v:
        v = []
    d += 1
    for c in x.components.copy():
        e.add((x, c, d))
        edges(c, e, v, d)
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

    @return: A directed graph representing x's Component structure.
    @rtype:  str
    """

    networkx = tryimport("networkx")
    pygraphviz = tryimport("pygraphviz")
    plt = tryimport("matplotlib.pyplot", "pyplot")

    if networkx is not None and pygraphviz is not None and plt is not None:
        graph_edges = []
        for (u, v, d) in edges(x):
            graph_edges.append((u.name, v.name, float(d)))

        g = networkx.DiGraph()
        g.add_weighted_edges_from(graph_edges)

        elarge = [(u, v) for (u, v, d) in g.edges(data=True)
                  if d["weight"] > 3.0]
        esmall = [(u, v) for (u, v, d) in g.edges(data=True)
                  if d["weight"] <= 3.0]

        pos = networkx.spring_layout(g)  # positions for all nodes

        # nodes
        networkx.draw_networkx_nodes(g, pos, node_size=700)

        # edges
        networkx.draw_networkx_edges(g, pos, edgelist=elarge, width=1)
        networkx.draw_networkx_edges(
            g, pos, edgelist=esmall, width=1,
            alpha=0.5, edge_color="b", style="dashed"
        )

        # labels
        networkx.draw_networkx_labels(
            g, pos, font_size=10, font_family="sans-serif"
        )

        plt.axis("off")

        plt.savefig("{0:s}.png".format(name or x.name))
        networkx.drawing.nx_agraph.write_dot(g, "{0:s}.dot".format(name or x.name))

        plt.clf()

    def printer(d, x):
        return "%s* %s" % (" " * d, x)

    return "\n".join(walk(x, printer))


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

    from circuits import reprhandler

    write(" Event Handlers: %d\n" % len(x._handlers.values()))
    for event, handlers in x._handlers.items():
        write("  %s; %d\n" % (event, len(x._handlers[event])))
        for handler in x._handlers[event]:
            write("   %s\n" % reprhandler(handler))

    return "".join(s)


def deprecated(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        warn_explicit(
            "Call to deprecated function {0:s}".format(f.__name__),
            category=DeprecationWarning,
            filename=getattr(f, _func_code).co_filename,
            lineno=getattr(f, _func_code).co_firstlineno + 1
        )
        return f(*args, **kwargs)
    return wrapper
