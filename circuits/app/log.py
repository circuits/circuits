# Filename: log.py
# Module:   log
# Date:     11th June 2006
# Author:   James Mills <prologic@shortcircuit.net.au>

"""Log

...
"""

import sys
import logging

from circuits import Event, Component

###
### Events
###

class Debug(Event):
    """Debug(Event) -> Debug Log Event

    args: msg
    """

class Info(Event):
    """Info(Event) -> Info Log Event

    args: msg
    """

class Warning(Event):
    """Warning(Event) -> Warning Log Event

    args: msg
    """

class Error(Event):
    """Error(Event) -> Error Log Event

    args: msg
    """

class Exception(Event):
    """Exception(Event) -> Exception Log Event

    args: msg
    """

class Critical(Event):
    """Critical(Event) -> Critical Log Event

    args: msg
    """

###
### Components
###

class Logger(Component):

    channel = "log"

    def __init__(self, filename, name, type, level, **kwargs):
        super(Logger, self).__init__(**kwargs)

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

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args):
        self.logger.exception(msg, *args)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
