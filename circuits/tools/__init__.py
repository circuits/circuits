# Module:	__init__
# Date:		8th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""

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

    s = []
    write = s.append

    d = 0
    i = 0
    done = False
    stack = []
    visited = set()
    children = list(x.components)
    while not done:
        if x not in visited:
            if d:
                write(" %s* %s\n" % (" " * d, x))
            else:
                write(" * %s\n" % x)

            if x.components:
                d += 1

            visited.add(x)

        if i < len(children):
            x = children[i]
            i += 1
            if x.components:
                stack.append((i, d, children))
                children = list(x.components)
                i = 0
        else:
            if stack:
                i, d, children = stack.pop()
            else:
                done = True

    return "".join(s)

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

    write("%s\n" % x)

    write(" Registered Components: %d\n" % len(x.components))
    for component in x.components:
        write("  %s\n" % component)
    write("\n")

    write(" Hidden Components: %d\n" % len(x.hidden))
    for component in x.hidden:
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

    return "".join(s)
