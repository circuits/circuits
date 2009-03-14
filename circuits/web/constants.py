# Module:   constants
# Date:     4th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Global Constants

This module implements required shared global constants.
"""

from BaseHTTPServer import BaseHTTPRequestHandler

from circuits import __version__

BUFFER_SIZE = 4096
SERVER_PROTOCOL = (1, 1)
SERVER_VERSION = "circuits/%s" % __version__

DEFAULT_ERROR_MESSAGE = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"></meta>
    <title>%(status)s</title>
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
        <h2>%(status)s</h2>
        <p>%(message)s</p>
        <pre id="traceback">%(traceback)s</pre>
    <div id="powered_by">
    <span>Powered by <a href="http://trac.softcircuit.com.au/circuits/">%(version)s</a></span>
    </div>
    </body>
</html>
"""

RESPONSES = BaseHTTPRequestHandler.responses.copy()

RESPONSES[500] = ("Internal Server Error",
        "The server encountered an unexpected condition "
        "which prevented it from fulfilling the request.")

RESPONSES[503] = ("Service Unavailable",
        "The server is currently unable to handle the "
        "request due to a temporary overloading or "
        "maintenance of the server.")
