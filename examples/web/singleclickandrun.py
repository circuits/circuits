#!/usr/bin/env python
import webbrowser

from circuits.web import Controller, Server


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
</html>
"""


class Root(Controller):

    def index(self):
        return HTML

    def exit(self):
        raise SystemExit(0)


app = Server(("0.0.0.0", 8000))
Root().register(app)
app.start()

webbrowser.open("http://127.0.0.1:8000/")
app.join()
