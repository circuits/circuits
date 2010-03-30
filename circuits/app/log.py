# Module:   logging
# Date:     11th June 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Logging Components"""

import sys
import logging
from logging import DEBUG, INFO, WARNING, WARN, ERROR, CRITICAL

from circuits.core import handler, Event, BaseComponent

class Log(Event):
    """Log Event"""

    channel = "log"
    target = "logger"

    success = "log_successful", target
    filter = "log_filtered", target
    failure = "log_failed", target

class Logger(BaseComponent):

    channel = "logger"

    LEVELS = {"debug": DEBUG, "info": INFO, "warning": WARNING,
            "warn": WARN, "error": ERROR, "exception": ERROR,
            "critical": CRITICAL}

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
        self.logger.log(self.LEVELS[level.lower()], msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
