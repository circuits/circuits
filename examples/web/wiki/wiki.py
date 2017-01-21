#!/usr/bin/env python
import os
import sqlite3

import macros
from creoleparser import Parser, create_dialect, creole11_base

import circuits
from circuits.web import Controller, Logger, Server, Static

text2html = Parser(
    create_dialect(creole11_base, macro_func=macros.dispatcher),
    method="xhtml"
)


class Wiki(object):

    def __init__(self, database):
        super(Wiki, self).__init__()

        create = not os.path.exists(database)

        self._cx = sqlite3.connect(database)
        self._cu = self._cx.cursor()

        if create:
            self._cu.execute("CREATE TABLE pages (name, text)")
            for defaultpage in os.listdir("defaultpages"):
                filename = os.path.join("defaultpages", defaultpage)
                self.save(defaultpage, open(filename, "r").read())

    def save(self, name, text):
        self._cu.execute("SELECT COUNT() FROM pages WHERE name=?", (name,))
        row = self._cu.fetchone()
        if row[0]:
            self._cu.execute(
                "UPDATE pages SET text=? WHERE name=?",
                (text, name,)
            )
        else:
            self._cu.execute(
                "INSERT INTO pages (name, text) VALUES (?, ?)",
                (name, text,)
            )
        self._cx.commit()

    def get(self, name, default=None):
        self._cu.execute("SELECT text FROM pages WHERE name=?", (name,))
        row = self._cu.fetchone()
        return row[0] if row else default


class Root(Controller):

    db = Wiki("wiki.db")

    environ = {"db": db, "macros": macros.loadMacros()}

    def GET(self, name="FrontPage", action="view"):
        environ = self.environ.copy()
        environ["page.name"] = name
        environ["parser"] = text2html

        d = {}
        d["title"] = name
        d["version"] = circuits.__version__
        d["menu"] = text2html(self.db.get("SiteMenu", ""), environ=environ)

        text = self.db.get(name, "")
        s = open("tpl/%s.html" % action, "r").read()

        if action == "view":
            d["text"] = text2html(text, environ=environ)
        else:
            d["text"] = text

        return s % d

    def POST(self, name="FrontPage", **form):
        self.db.save(name, form.get("text", ""))
        return self.redirect(name)


app = Server(("0.0.0.0", 9000))
Static(docroot="static").register(app)
Root().register(app)
Logger().register(app)
app.run()
