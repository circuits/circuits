"""Macros macros

Macros to display information about other macros
"""

def macros(macro, environ, *args, **kwargs):
    """Return a list of available macros"""

    s = StringIO()

    s.write("= Available Macros =\n")
    s.write("\N")

    for k, v in environ["macros"].items():
        s.write("* %s\n" % (k))
    s.write("\n")

    v = s.getvalue()
    s.close()

    return v
