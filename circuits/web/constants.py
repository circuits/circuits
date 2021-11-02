"""
Global Constants

This module implements required shared global constants.
"""

from circuits import __version__


SERVER_PROTOCOL = (1, 1)
SERVER_VERSION = 'circuits.web/%s' % __version__
SERVER_URL = 'http://circuitsweb.com/'

DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>
  <title>%(code)d %(name)s</title>
  <style type="text/css">
   #powered_by {
    margin-top: 20px;
    border-top: 2px solid black;
    font-style: italic;
   }

   #traceback {
    color: red;
   }
  </style>
 </head>
 <body>
  <h1>%(name)s</h1>
  %(description)s
  <pre id="traceback">%(traceback)s</pre>
  %(powered_by)s
 </body>
</html>
"""

POWERED_BY = """
<div id="powered_by">
    <span>Powered by <a href="%(url)s">%(version)s</a></span>
</div>
"""
