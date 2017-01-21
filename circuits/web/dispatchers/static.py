"""Static

This modStatic implements a Static dispatcher used to serve up static
resources and an optional apache-style directory listing.
"""
import os
from string import Template

from circuits import BaseComponent, handler
from circuits.six.moves.urllib_parse import quote, unquote
from circuits.web.tools import serve_file

DEFAULT_DIRECTORY_INDEX_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
        <meta http-equiv="Content-Language" content="en-us" />
        <meta name="robots" content="NONE,NOARCHIVE" />
        <title>Index of $directory</title>
    </head>
    <body>
        <h1>Index of $directory</h1>
        <ul>
            $url_up
            $listing
        </ul>
    </body>
</html>
"""

_dirlisting_template = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE)


class Static(BaseComponent):

    channel = "web"

    def __init__(self, path=None, docroot=None,
                 defaults=("index.html", "index.xhtml",), dirlisting=False, **kwargs):
        super(Static, self).__init__(**kwargs)

        self.path = path
        self.docroot = os.path.abspath(
            docroot) if docroot is not None else os.path.abspath(os.getcwd())
        self.defaults = defaults
        self.dirlisting = dirlisting

    @handler("request", priority=0.9)
    def _on_request(self, event, request, response):
        if self.path is not None and not request.path.startswith(self.path):
            return

        path = request.path

        if self.path is not None:
            path = path[len(self.path):]

        path = unquote(path.strip("/"))

        if path:
            location = os.path.abspath(os.path.join(self.docroot, path))
        else:
            location = os.path.abspath(os.path.join(self.docroot, "."))

        if not os.path.exists(location):
            return

        if not location.startswith(os.path.dirname(self.docroot)):
            return  # hacking attemp e.g. /foo/../../../../../etc/shadow

        # Is it a file we can serve directly?
        if os.path.isfile(location):
            # Don't set cookies for static content
            response.cookie.clear()
            try:
                return serve_file(request, response, location)
            finally:
                event.stop()

        # Is it a directory?
        elif os.path.isdir(location):

            # Try to serve one of default files first..
            for default in self.defaults:
                location = os.path.abspath(
                    os.path.join(self.docroot, path, default)
                )
                if os.path.exists(location):
                    # Don't set cookies for static content
                    response.cookie.clear()
                    try:
                        return serve_file(request, response, location)
                    finally:
                        event.stop()

            # .. serve a directory listing if allowed to.
            if self.dirlisting:
                directory = os.path.abspath(os.path.join(self.docroot, path))
                cur_dir = os.path.join(self.path, path) if self.path else ""

                if not path:
                    url_up = ""
                else:
                    if self.path is None:
                        url_up = os.path.join("/", os.path.split(path)[0])
                    else:
                        url_up = os.path.join(cur_dir, "..")
                    url_up = '<li><a href="%s">%s</a></li>' % (url_up, "..")

                listing = []
                for item in os.listdir(directory):
                    if not item.startswith("."):
                        url = os.path.join("/", path, cur_dir, item)
                        location = os.path.abspath(
                            os.path.join(self.docroot, path, item)
                        )
                        if os.path.isdir(location):
                            li = '<li><a href="%s/">%s/</a></li>' % (
                                quote(url), item
                            )
                        else:
                            li = '<li><a href="%s">%s</a></li>' % (
                                quote(url), item
                            )
                        listing.append(li)

                ctx = {}
                ctx["directory"] = cur_dir or os.path.join("/", cur_dir, path)
                ctx["url_up"] = url_up
                ctx["listing"] = "\n".join(listing)
                try:
                    return _dirlisting_template.safe_substitute(ctx)
                finally:
                    event.stop()
