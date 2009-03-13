# Module:	__init__
# Date:		8th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""

def walk(x, f, d=0):
    yield f(d, x)
    for c in x.components.copy():
        for r in walk(c, f, d + 1):
            yield r

def root(x):
    if x.manager == x:
        return x
    else:
        return root(x.manager)

def kill(x):
    for c in x.components.copy():
        kill(c)
    x.unregister()

def graph(x):
    """Display a directed graph of the Component structure of x

    @param x: A Component or Manager to graph
    @type  x: Component or Manager

    @return: A directed graph representing x's Component sturcture.
    @rtype:  str
    """

    def printer(d, x):
        return "%s* %s" % (" " * d, x)

    return "\n".join(walk(x, printer))
    
def reprhandler(x):
    """Display a nicely formatted Event Handler, x

    @param x: An Event Handler
    @type  x: function or method

    @return: A nicely formatted representation of the Event Handler, x
    @rtype:  str
    """

    if not hasattr(x, "handler"):
        raise TypeError("%r is not an Event Handler" % x)

    format = "<handler %r {filter: %s, target: %s) of %s>"
    component = getattr(x, "im_self", None)
    return format % (x.channels, x.filter, x.target, component)

def inspect(x):
    """Display an inspection report of the Component or Manager x

    @param x: A Component or Manager to graph
    @type  x: Component or Manager

    @return: A detailed inspection report of x
    @rtype:  str
    """

    s = []
    write = s.append

    write(" Registered Components: %d\n" % len(x.components))
    for component in x.components:
        write("  %s\n" % component)
    write("\n")

    write(" Tick Functions: %d\n" % len(x.ticks))
    for tick in x.ticks:
        write("  %s\n" % tick)
    write("\n")

    write(" Channels and Event Handlers: %d\n" % len(x.channels))
    for channel in x.channels:
        write("  %s: %d\n" % (channel, len(x.channels[channel])))
        for handler in x.channels[channel]:
            write("   %s\n" % reprhandler(handler))
    write("\n")

    return "".join(s)
