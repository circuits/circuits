# Module:   logging
# Date:     11th June 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Logging Components"""

import sys
import logging
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING


from circuits.core import handler, Event, BaseComponent

class Log(Event):
    """Log Event"""

    channel = "log"
    target = "log"

    success = "log_successful", "log"
    filter = "log_filtered", "log"
    failure = "log_failed", "log"

class Logger(BaseComponent):

    channel = "log"

    def __init__(self, filename, name, type, level, channel=channel):
        super(Logger, self).__init__(channel=channel)

        self.logger = logging.getLogger(name)

        type = type.lower()
        if type == "file":
            hdlr = logging.FileHandler(filename)
        elif type in ["winlog", "eventlog", "nteventlog"]:
            # Requires win32 extensions
            hdlr = logging.handlers.NTEventLogHandler(name, type="Application")
        elif type in ["syslog", "unix"]:
            hdlr = logging.handlers.SysLogHandler("/dev/log")
        elif type in ["stderr"]:
            hdlr = logging.StreamHandler(sys.stderr)
        else:
            raise ValueError

        format = name + "[%(module)s] %(levelname)s: %(message)s"
        if type == "file":
            format = "%(asctime)s " + format
        dateFormat = ""
        level = level.upper()
        if level in ["DEBUG", "ALL"]:
            self.logger.setLevel(logging.DEBUG)
            dateFormat = "%X"
        elif level == "INFO":
            self.logger.setLevel(logging.INFO)
        elif level == "ERROR":
            self.logger.setLevel(logging.ERROR)
        elif level == "CRITICAL":
            self.logger.setLevel(logging.CRITICAL)
        else:
            self.logger.setLevel(logging.WARNING)

        formatter = logging.Formatter(format,dateFormat)
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)

    @handler("log")
    def log(self, level, msg, *args, **kwargs):
        self.logger.log(level, msg, *args, **kwargs)
        return True
