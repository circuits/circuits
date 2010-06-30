"""HTML macros

Macros for generating snippets of HTML.
"""

import genshi
import pygments
import pygments.util
import pygments.lexers
import pygments.formatters
from genshi.filters import HTMLSanitizer

sanitizer = HTMLSanitizer()

def code(macro, environ, *args, **kwargs):
    """Render syntax highlighted code"""
    
    if not macro.body:
        return None

    lang = kwargs.get("lang", None)

    if lang is not None:
        if not macro.isblock:
            return None
        try:
            lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
        except pygments.util.ClassNotFound:
            return None
    else:
        lexer = None

    if lexer:
        text = pygments.highlight(macro.body, lexer,
                pygments.formatters.HtmlFormatter())
        output = genshi.core.Markup(text)
    elif macro.isblock:
        output = genshi.builder.tag.pre(macro.body)
    else:
        output = genshi.builder.tag.code(macro.body,
                style="white-space:pre-wrap", class_="highlight")

    return output

def source(macro, environ, *args, **kwargs):
    """Return the parsed text of body, rendered in a <pre> block."""
    
    if macro.body is None:
        return None

    return builder.tag.pre(environ["parser"].render(
        macro.body, environ=environ).decode("utf-8"))

def div(macro, environ, class_=None, float=None, id=None, style=None,
        *args, **kwargs):
    """..."""

    if macro.body is None:
        return None

    if float and float in ("left", "right"):
        style = "float: %s; %s" % (float, style)

    if style:
        style = ';'.join(sanitizer.sanitize_css(style))

    if macro.isblock:
        context = 'block'
    else:
        context = 'inline'

    contents = environ['parser'].generate(
            macro.body, environ=environ, context=context)

    return builder.tag.div(contents, id=id, class_=class_, style=style)

def span(macro, environ, class_=None, id=None, style=None, *args, **kwargs):
    """..."""

    if macro.body is None:
        return None

    if style:
        style = ';'.join(sanitizer.sanitize_css(style))

    contents = environ['parser'].generate(
            macro.body, environ=environ, context='inline')

    return builder.tag.span(contents, id=id, class_=class_,style=style)
