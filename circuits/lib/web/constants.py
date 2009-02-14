# Module:   constants
# Date:     4th February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Global Constants

This module implements required shared global constants.
"""

from circuits import __version__

BUFFER_SIZE = 131072
SERVER_PROTOCOL = "HTTP/1.1"
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

RESPONSES = {
    100: ("Continue", "Request received, please continue"),
    101: ("Switching Protocols",
        "Switching to new protocol; obey Upgrade header"),

    200: ("OK", "Request fulfilled, document follows"),
    201: ("Created", "Document created, URL follows"),
    202: ("Accepted",
        "Request accepted, processing continues off-line"),
    203: ("Non-Authoritative Information", "Request fulfilled from cache"),
    204: ("No Content", "Request fulfilled, nothing follows"),
    205: ("Reset Content", "Clear input form for further input."),
    206: ("Partial Content", "Partial content follows."),

    300: ("Multiple Choices",
        "Object has several resources -- see URI list"),
    301: ("Moved Permanently", "Object moved permanently -- see URI list"),
    302: ("Found", "Object moved temporarily -- see URI list"),
    303: ("See Other", "Object moved -- see Method and URL list"),
    304: ("Not Modified",
        "Document has not changed since given time"),
    305: ("Use Proxy",
        "You must use proxy specified in Location to access this "
        "resource."),
    307: ("Temporary Redirect",
        "Object moved temporarily -- see URI list"),

    400: ("Bad Request",
        "Bad request syntax or unsupported method"),
    401: ("Unauthorized",
        "No permission -- see authorization schemes"),
    402: ("Payment Required",
        "No payment -- see charging schemes"),
    403: ("Forbidden",
        "Request forbidden -- authorization will not help"),
    404: ("Not Found", "Nothing matches the given URI"),
    405: ("Method Not Allowed",
        "Specified method is invalid for this server."),
    406: ("Not Acceptable", "URI not available in preferred format."),
    407: ("Proxy Authentication Required", "You must authenticate with "
        "this proxy before proceeding."),
    408: ("Request Timeout", "Request timed out; try again later."),
    409: ("Conflict", "Request conflict."),
    410: ("Gone",
        "URI no longer exists and has been permanently removed."),
    411: ("Length Required", "Client must specify Content-Length."),
    412: ("Precondition Failed", "Precondition in headers is false."),
    413: ("Request Entity Too Large", "Entity is too large."),
    414: ("Request-URI Too Long", "URI is too long."),
    415: ("Unsupported Media Type", "Entity body in unsupported format."),
    416: ("Requested Range Not Satisfiable",
        "Cannot satisfy request range."),
    417: ("Expectation Failed",
        "Expect condition could not be satisfied."),

    500: ("Internal Server Error", "Server got itself in trouble"),
    501: ("Not Implemented",
        "Server does not support this operation"),
    502: ("Bad Gateway", "Invalid responses from another server/proxy."),
    503: ("Service Unavailable",
        "The server cannot process the request due to a high load"),
    504: ("Gateway Timeout",
        "The gateway server did not receive a timely response"),
    505: ("HTTP Version Not Supported", "Cannot fulfill request."),
}
