#!/usr/bin/env python

import webbrowser

from circuits.web import Server, Controller

HTML = """\
<html>
 <head>
  <title>An example application</title>
 </head>
<body>
 <h1>This is my sample application</h1>
 Put the content here...
 <hr>
 <a href="/exit">Quit</a>
</body>
</html>"""

class Root(Controller):

    def index(self):
        return HTML

    def exit(self):
        raise SystemExit(0)

server = (Server(8000) + Root())
server.start()

webbrowser.open("http://127.0.0.1:8000/")
server.join()
