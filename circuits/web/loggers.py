# Module:   loggers
# Date:     6th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Logger Component

This module implements Logger Components.
"""

import os
import sys
import rfc822
import datetime

from circuits.core import handler, BaseComponent

def formattime():
    now = datetime.datetime.now()
    month = rfc822._monthnames[now.month - 1].capitalize()
    return ("[%02d/%s/%04d:%02d:%02d:%02d]" %
            (now.day, month, now.year, now.hour, now.minute, now.second))

class Logger(BaseComponent):

    channel = "web"

    format = "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\""

    def __init__(self, file=None, logger=None, **kwargs):
        super(Logger, self).__init__(**kwargs)

        if type(file) is str:
            self.file = open(os.path.abspath(os.path.expanduser(file)), "a")
        elif type(file) is file or hasattr(file, "write"):
            self.file = file
        else:
            self.file = sys.stdout

        self.logger = logger

    @handler("response")
    def response(self, response):
        self.log(response)

    def log(self, response):
        request = response.request
        remote = request.remote
        outheaders = response.headers
        inheaders = request.headers

        protocol = "HTTP/%d.%d" % request.protocol
        
        if "X-Forwarded-For" in inheaders:
            host = inheaders["X-Forwarded-For"]
        else:
            host = remote.name or remote.ip

        atoms = {"h": host,
                 "l": "-",
                 "u": getattr(request, "login", None) or "-",
                 "t": formattime(),
                 "r": "%s %s %s" % (request.method, request.path, protocol),
                 "s": str(response.code),
                 "b": outheaders.get("Content-Length", "") or "-",
                 "f": inheaders.get("Referer", ""),
                 "a": inheaders.get("User-Agent", ""),
                 }
        for k, v in atoms.items():
            if isinstance(v, unicode):
                v = v.encode("utf8")
            elif not isinstance(v, str):
                v = str(v)
            # Fortunately, repr(str) escapes unprintable chars, \n, \t, etc
            # and backslash for us. All we have to do is strip the quotes.
            v = repr(v)[1:-1]
            # Escape double-quote.
            atoms[k] = v.replace("\"", "\\\"")

        if self.logger is not None:
            self.logger.info(self.format % atoms)
        else:
            self.file.write(self.format % atoms)
            self.file.write("\n")
            self.file.flush()

