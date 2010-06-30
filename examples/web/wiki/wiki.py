#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
                self[defaultpage] = open(filename, "r").read()

    def __contains__(self, name):
        self._cu.execute("SELECT COUNT() AS result FROM pages WHERE name=?",
                (name,))
        row = self._cu.fetchone()
        return row[0]

    def __getitem__(self, name):
        self._cu.execute("SELECT text FROM pages WHERE name=?", (name,))
        row = self._cu.fetchone()
        return row[0]

    def __setitem__(self, name, text):
        if name in self:
            self._cu.execute("UPDATE pages SET text=? WHERE name=?",
                    (text, name,))
        else:
            self._cu.execute("INSERT INTO pages (name, text) VALUES (?, ?)",
                    (name, text,))

        self._cx.commit()

    def get(self, name, default=None):
        return self.__getitem__(name) if name in self else default

class Root(Controller):

    def __init__(self, db):
        super(Root, self).__init__()
        self.db = db

    def GET(self, name="FrontPage", action="view"):
        d = {}
        d["title"] = name
        d["version"] = circuits.__version__
        d["menu"] = creoleparser.text2html(self.db.get("SiteMenu", ""))

        text = self.db.get(name, "")
        s = open("tpl/%s.html" % action, "r").read()

        if action == "view":
            d["page"] = creoleparser.text2html(text)
        elif action == "edit":
            d["text"] = text

        return s % d

    def POST(self, name, **form):
        self.db[name] = form.get("text", "")
        return self.redirect(name)

db = Wiki("wiki.db")

(Server(("0.0.0.0", 8000))
        + Static(docroot="static")
        + Root(db)
        + Logger()).run()
