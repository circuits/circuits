"""Wiki macros"""

from genshi import builder

def title(macro, environ, *args, **kwargs):
    """Return the title of the current page."""

    return builder.tag(environ["page.name"])

def pre(macro, environ, *args, **kwargs):
    """Return the raw text of body, rendered in a <pre> block."""
    
    if macro.body is None:
        return None
    return builder.tag.pre(macro.body)
