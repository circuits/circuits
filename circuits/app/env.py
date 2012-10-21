# Module:   env
# Date:     10th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Environment Component

An Environment Component that by default sets up a Config and Logger
components and is used to create, load and manage system/application
environments.
"""

from os import mkdir
from os import makedirs
from signal import SIGHUP
from os.path import abspath, isabs, join as joinpath

from circuits import handler, BaseComponent, Event

from . import config
from .config import Config

from .log import Logger


VERSION = 1

CONFIG = {
    "general": {
        "pidfile": joinpath("%(path)s", "log", "%(name)s.pid"),
    },
    "logging": {
        "debug": "True",
        "type": "file",
        "verbose": "True",
        "level": "DEBUG",
        "file": joinpath("%(path)s", "log", "%(name)s.log"),
    }
}

ERRORS = (
    (0, "No Environment version information",),
    (1, "Environment needs upgrading",),
)


def createFile(filename, data=None):
    fd = open(filename, "w")
    if data:
        fd.write(data)
    fd.close()


class EnvironmentError(Exception):
    """Environment Error"""


class EnvironmentEvent(Event):
    """Environment Event"""

    channels = ("env",)


class Ready(EnvironmentEvent):
    """Ready Environment Event"""


class Create(EnvironmentEvent):
    """Create Environment Event"""

    success = True
    failure = True


class Load(EnvironmentEvent):
    """Load Environment Event"""

    success = True
    failure = True


class Verify(EnvironmentEvent):
    """Verify Environment Event"""

    success = True
    failure = True


class Upgrade(EnvironmentEvent):
    """Upgrade Environment Event"""

    success = True
    failure = True


class Environment(BaseComponent):
    """Base Environment Component

    Creates a new environment component that by default only
    holds configuration and logger components.

    This component can be extended to provide more complex
    system and application environments.
    """

    channel = "env"

    version = VERSION

    def __init__(self, path, envname, channel=channel):
        super(Environment, self).__init__(channel=channel)

        self.path = abspath(path)
        self.envname = envname

    @handler("create", priority=1.0)
    def create(self):
        return self._create()

    @handler("load", priority=1.0)
    def load(self, verify=False):
        if verify:
            return self.fire(Verify())
        else:
            return self._load()

    @handler("verify", priority=1.0)
    def _on_verify(self):
        f = open(joinpath(self.path, "VERSION"), "r")
        version = f.read().strip()
        f.close()

        if not version:
            raise EnvironmentError(*ERRORS[0])
        else:
            if self.version > int(version):
                raise EnvironmentError(*ERRORS[1])

    @handler("verify_success", filter=True)
    def _on_verify_success(self, evt, retval):
        return self._load()

    @handler("load_success", channel="config")
    def _on_config_load_success(self, evt, retval):
        # Create Logger Component
        logname = self.envname
        logtype = self.config.get("logging", "type", "file")
        loglevel = self.config.get("logging", "level", "INFO")
        logfile = self.config.get("logging", "file", "/dev/null")
        logfile = logfile % {"name": self.envname}
        if not isabs(logfile):
            logfile = joinpath(self.path, logfile)
        self.log = Logger(logfile, logname, logtype, loglevel).register(self)
        self.fire(Ready())

    def _create(self):
        # Create the directory structure
        makedirs(self.path)
        mkdir(joinpath(self.path, "log"))
        mkdir(joinpath(self.path, "conf"))

        # Create a few files
        createFile(joinpath(self.path, "VERSION"), "%d" % self.version)
        createFile(
                joinpath(self.path, "README"),
                "This directory contains a %s Environment." % self.envname
        )

        # Setup the default configuration
        configfile = joinpath(self.path, "conf", "%s.ini" % self.envname)
        createFile(configfile)
        self.config = Config(configfile).register(self)
        for section in CONFIG:
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in CONFIG[section].items():
                if type(value) == str:
                    value = value % {
                        "name": self.envname,
                        "path": self.path,
                    }
                self.config.set(section, option, value)
        return self.fire(config.Save(), self.config)

    def _load(self):
        # Create Config Component
        configfile = joinpath(self.path, "conf", "%s.ini" % self.envname)
        self.config = Config(configfile).register(self)
        self.fire(config.Load())
        return True
