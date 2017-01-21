"""Global Constants

This module implements required shared global constants.
"""
from circuits import __version__

SERVER_PROTOCOL = (1, 1)
SERVER_VERSION = "circuits.web/%s" % __version__
SERVER_URL = "http://circuitsweb.com/"

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

HTTP_STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi Status",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I\"m a teapot",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    426: "Upgrade Required",
    449: "Retry With",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    507: "Insufficient Storage",
    510: "Not Extended"
}
