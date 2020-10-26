#!/usr/bin/env python
import os

import mako
from mako.lookup import TemplateLookup

from circuits.web import Controller, Server, Static

DEFAULTS = {}

templates = TemplateLookup(
    directories=[os.path.join(os.path.dirname(__file__), "tpl")],
    module_directory="/tmp",
    output_encoding="utf-8"
)


def render(name, **d):
    try:
        d.update(DEFAULTS)
        tpl = templates.get_template(name)
        return tpl.render(**d)
    except Exception:
        return mako.exceptions.html_error_template().render()


class Root(Controller):

    tpl = "index.html"

    def index(self):
        return render(self.tpl)

    def submit(self, firstName, lastName):
        msg = "Thank you %s %s" % (firstName, lastName)
        return render(self.tpl, message=msg)


app = Server(("0.0.0.0", 8000))
Static().register(app)
Root().register(app)
app.run()
