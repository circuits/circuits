"""Code macros

Macros for displaying code with syntax highlighting
"""

import re

import genshi
import pygments
import pygments.util
import pygments.lexers
import pygments.formatters

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
