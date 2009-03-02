# Module:	__init__
# Date:		8th November 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits Tools

circuits.tools contains a standard set of tools for circuits. These
tools are installed as executables with a prefix of "circuits."
"""

def graph(x):
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
                write("%s%s\n" % (" " * d, "|"))
                write("%s%s%s\n" % (" " * d, "|-", x))
            else:
                write(" .%s\n" % x)

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
    if not hasattr(x, "handler"):
        raise TypeError("%r is not an Event Handler" % x)

    format = "<handler %r {filter: %s, target: %s) of %s>"
    component = getattr(x, "im_self", None)
    return format % (x.channels, x.filter, x.target, component)

def inspect(x):
    s = []
    write = s.append

    write("%s\n" % x)

    write(" Registered Components:")
    if x.components:
        for component in x.components:
            write("\n  %s" % component)
    else:
        write(" None")
    write("\n")

    write(" Hidden Components:")
    if x.hidden:
        for component in x.hidden:
            write("\n  %s" % component)
    else:
        write(" None")
    write("\n")

    write(" Tick Functions:")
    if x.ticks:
        for tick in x.ticks:
            write("\n  %s" % tick)
    else:
        write(" None")
    write("\n")

    write(" Channels and Event Handlers:")
    if x.channels:
        for channel in x.channels:
            write("\n  %s:" % channel)
            if x.channels[channel]:
                for handler in x.channels[channel]:
                    write("\n   %s" % reprhandler(handler))
            else:
                write(" None")
    else:
        write(" None")
    write("\n")

    return "".join(s)
