"""Wiki macros"""

from genshi import builder


def title(macro, environ, *args, **kwargs):
    """Return the title of the current page."""

    return builder.tag(environ["page.name"])
