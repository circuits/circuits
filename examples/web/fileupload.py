#!/usr/bin/env python

from circuits import Debugger
from circuits.web import Server, Controller

UPLOAD_FORM = """
<html>
 <head>
  <title>Upload Form</title>
 </head>
 <body>
  <h1>Upload Form</h1>
  <form method="POST" action="/" enctype="multipart/form-data">
   Description: <input type="text" name="desc"><br>
   <input type="file" name="file">
   <input type="submit" value="Submit">
  </form>
 </body>
</html>
"""

UPLOADED_FILE = """
<html>
 <head>
  <title>Uploaded File</title>
 </head>
 <body>
  <h1>Uploaded File</h1>
  <p>
   Filename: %s<br>
   Description: %s
  </p>
  <p><b>File Contents:</b></p>
  <pre>
  %s
  </pre>
 </body>
</html>
"""

class Root(Controller):

    def index(self, file=None, desc=""):
        if file is None:
            return UPLOAD_FORM
        else:
            filename = file.filename
            return UPLOADED_FILE % (file.filename, desc, file.value)

(Server(8000) + Debugger() + Root()).run()
