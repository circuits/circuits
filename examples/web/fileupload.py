#!/usr/bin/env python
"""File Upload

A simple example showing how to access an uploaded file.
"""
from circuits.web import Controller, Server


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
        """Request Handler

        If we haven't received an uploaded file yet, repond with
        the UPLOAD_FORM template. Otherwise respond with the
        UPLOADED_FILE template. The file is accessed through
        the ``file`` keyword argument and the description via
        the ``desc`` keyword argument. These also happen to be
        the same fields used on the form.
        """

        if file is None:
            return UPLOAD_FORM
        else:
            return UPLOADED_FILE % (file.filename, desc, file.value)


app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
