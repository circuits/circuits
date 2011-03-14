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

from .log import Logger
from .config import Config, LoadConfig, SaveConfig


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


def createFile(filename, data=None):
    fd = open(filename, "w")
    if data:
        fd.write(data)
    fd.close()


class InvalidEnvironmentError(Exception):
    """Invalid Environment Error"""


class UpgradeEnvironmentError(Exception):
    """Upgrade Environment Error"""


class EnvironmentEvent(Event):
    """Environment Event"""

    _target = "env"


class CreateEnvironment(EnvironmentEvent):
    """Create Environment Event"""

    channel = "create_environment"

    start = "creating_environment", EnvironmentEvent._target
    end = "environment_created", EnvironmentEvent._target


class LoadEnvironment(EnvironmentEvent):
    """Load Environment Event"""

    channel = "load_environment"

    start = "loading_environment", EnvironmentEvent._target


class EnvironmentLoaded(EnvironmentEvent):
    """Environment Loaded Event"""

    channel = "environment_loaded"


class VerifyEnvironment(EnvironmentEvent):
    """Verify EEnvironment Event"""

    channel = "verify_environment"

    start = "verifying_environment", EnvironmentEvent._target
    success = "environment_verified", EnvironmentEvent._target
    failure = "environment_invalid", EnvironmentEvent._target


class UpgradeEnvironment(EnvironmentEvent):
    """Upgrade Environment Event"""

    channel = "upgrade_environment"

    start = "upgrading_environment", EnvironmentEvent._target
    end = "environment_upgraded", EnvironmentEvent._target


class BaseEnvironment(BaseComponent):
    """Base Environment Component

    Creates a new environment component that by default only
    holds configuration and logger components.

    This component can be extended to provide more complex
    system and application environments.
    """

    channel = "env"

    version = VERSION

    def __init__(self, path, envname, channel=channel):
        super(BaseEnvironment, self).__init__(channel=channel)

        self.path = abspath(path)
        self.envname = envname

    def _load(self):
        # Create Config Component
        configfile = joinpath(self.path, "conf", "%s.ini" % self.envname)
        self.config = Config(configfile).register(self)
        self.push(LoadConfig(), target=self.config)

    @handler("create_environment")
    def _on_create_environment(self):
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
        self.push(SaveConfig(), target=self.config)

    @handler("verify_environment")
    def _on_verify_environment(self):
        f = open(joinpath(self.path, "VERSION"), "r")
        version = f.read().strip()
        f.close()

        if not version:
            msg = "No Environment version information"
            raise InvalidEnvironmentError(msg)
        else:
            if self.version > int(version):
                msg = "Environment needs upgrading"
                raise UpgradeEnvironmentError(msg)

    @handler("environment_verified")
    def _on_verify_pass(self, evt, handler, retval):
        self._load()

    @handler("environment_invalid")
    def _on_environment_invalid(self, evt, handler, error):
        raise SystemExit(-1)

    @handler("load_environment")
    def _on_load_environment(self, verify=False):
        if verify:
            self.push(VerifyEnvironment())
        else:
            self._load()

    @handler("config_loaded", target="config")
    def _on_config_loaded(self, evt, handler, retval):
        # Create Logger Component
        logname = self.envname
        logtype = self.config.get("logging", "type", "file")
        loglevel = self.config.get("logging", "level", "INFO")
        logfile = self.config.get("logging", "file", "/dev/null")
        logfile = logfile % {"name": self.envname}
        if not isabs(logfile):
            logfile = joinpath(self.path, logfile)
        self.log = Logger(logfile, logname, logtype, loglevel).register(self)
        self.push(EnvironmentLoaded())

    @handler("signal", target="*")
    def signal(self, signal, track):
        if signal == SIGHUP:
            self._load()
