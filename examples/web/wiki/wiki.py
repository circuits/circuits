#!/usr/bin/env python

import os
import sqlite3

import creoleparser

import circuits
from circuits.web import Server, Controller, Logger, Static

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
        self._cu.execute("SELECT name FROM pages WHERE name=?", (name,))
        if self._cu.rowcount:
            self._cu.execute("UPDATE pages SET text=? WHERE name=?",
                    (text, name,))
        else:
            self._cu.execute("INSERT INTO pages (name, text) VALUES (?, ?)",
                    (name, text,))
        self._cx.commit()

    def get(self, name, default=None):
        self._cu.execute("SELECT text FROM pages WHERE name=?", (name,))
        row = self._cu.fetchone()
        return row[0] if row else default

class Root(Controller):

    db = Wiki("wiki.db")

    def GET(self, name="FrontPage", action="view"):
        d = {}
        d["title"] = name
        d["version"] = circuits.__version__
        d["menu"] = creoleparser.text2html(self.db.get("SiteMenu", ""))

        text = self.db.get(name, "")
        s = open("tpl/%s.html" % action, "r").read()

        d["text"] = creoleparser.text2html(text) if action == "view" else text

        return s % d

    def POST(self, name, **form):
        self.db.save(name, form.get("text", ""))
        return self.redirect(name)

(Server(("0.0.0.0", 8000)) + Static(docroot="static") + Root() + Logger()).run()
