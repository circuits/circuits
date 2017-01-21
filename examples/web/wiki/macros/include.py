"""Include macros

Macros for inclusion of other wiki pages
"""
from genshi import builder


def include(macro, environ, pagename=None, *args, **kwargs):
    """Return the parsed content of the page identified by arg_string"""

    if pagename is None:
        return None

    db = environ["db"]
    page = db.get(pagename, None)

    if page is not None:
        environ["page.name"] = pagename

        return environ["parser"].generate(page, environ=environ)


def include_raw(macro, environ, pagename=None, *args, **kwargs):
    """Return the raw text of the page identified by arg_string, rendered
    in a <pre> block.
    """

    if pagename is None:
        return None

    db = environ["db"]
    page = db.get(pagename, None)

    if page is not None:
        return builder.tag.pre(page, class_="plain")


def include_source(macro, environ, pagename=None, *args, **kwargs):
    """Return the parsed text of the page identified by arg_string, rendered
    in a <pre> block.
    """

    if pagename is None:
        return None

    db = environ["db"]
    page = db.get(pagename, None)

    if page is not None:
        environ["page.name"] = pagename

        return builder.tag.pre(environ["parser"].render(
            page, environ=environ).decode("utf-8")
        )
