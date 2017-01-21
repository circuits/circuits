"""Logger Component

This module implements Logger Components.
"""
import datetime
import os
import sys
from io import IOBase

from circuits.core import BaseComponent, handler
from circuits.six import string_types, text_type


def formattime():
    return datetime.datetime.now().strftime('[%d/%b/%Y:%H:%M:%S]')


class Logger(BaseComponent):

    channel = "web"

    format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

    def __init__(self, file=None, logger=None, **kwargs):
        super(Logger, self).__init__(**kwargs)

        if isinstance(file, string_types):
            self.file = open(os.path.abspath(os.path.expanduser(file)), "a")
        elif isinstance(file, IOBase) or hasattr(file, "write"):
            self.file = file
        else:
            self.file = sys.stdout

        self.logger = logger

    @handler("response_success")
    def log_response(self, response_event, value):
        response = response_event.args[0]
        self.log(response)

    def log(self, response):
        request = response.request
        remote = request.remote
        outheaders = response.headers
        inheaders = request.headers or {}

        protocol = "HTTP/%d.%d" % request.protocol

        host = inheaders.get("X-Forwarded-For", (remote.name or remote.ip))

        atoms = {"h": host,
                 "l": "-",
                 "u": getattr(request, "login", None) or "-",
                 "t": formattime(),
                 "r": "%s %s %s" % (request.method, request.path, protocol),
                 "s": int(response.status),
                 "b": outheaders.get("Content-Length", "") or "-",
                 "f": inheaders.get("Referer", ""),
                 "a": inheaders.get("User-Agent", ""),
                 }
        for k, v in list(atoms.items()):
            if isinstance(v, text_type):
                v = v.encode("utf8")
            elif not isinstance(v, str):
                v = str(v)
            # Fortunately, repr(str) escapes unprintable chars, \n, \t, etc
            # and backslash for us. All we have to do is strip the quotes.
            v = repr(v)[1:-1]
            # Escape double-quote.
            atoms[k] = v.replace('"', '\\"')

        if self.logger is not None:
            self.logger.info(self.format % atoms)
        else:
            self.file.write(self.format % atoms)
            self.file.write("\n")
            self.file.flush()
