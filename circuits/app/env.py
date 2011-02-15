# Module:   env
# Date:     10th June 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Environment Component

An Environment Component that by default sets up a Config and Logger
components and is used to create, load and manage system/application
environments.
"""


import os

from circuits import handler, BaseComponent, Event

from log import Logger
from config import Config, LoadConfig, SaveConfig


VERSION = 1

CONFIG = {
        "general": {
            "pidfile": os.path.join("log", "%(name)s.pid"),
        },
        "logging": {
            "debug": True,
            "type": "file",
            "verbose": True,
            "level": "DEBUG",
            "file": os.path.join("log", "%(name)s.log"),
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

        self.path = os.path.abspath(os.path.expanduser(path))
        self.envname = envname

    def _load(self):
        os.chdir(self.path)

        # Create Config Component
        configfile = os.path.join(self.path, "conf", "%s.ini" % self.envname)
        self.config = Config(configfile).register(self)
        self.push(LoadConfig(), target=self.config)

    @handler("create_environment")
    def _on_create_environment(self):
        # Create the directory structure
        os.makedirs(self.path)
        os.chdir(self.path)
        os.mkdir(os.path.join(self.path, "log"))
        os.mkdir(os.path.join(self.path, "conf"))

        # Create a few files
        createFile(os.path.join(self.path, "VERSION"), "%d" % self.version)
        createFile(
                os.path.join(self.path, "README"),
                "This directory contains a %s Environment." % self.envname
        )

        # Setup the default configuration
        configfile = os.path.join(self.path, "conf", "%s.ini" % self.envname)
        createFile(configfile)
        self.config = Config(configfile).register(self)
        for section in CONFIG:
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option, value in CONFIG[section].iteritems():
                if type(value) == str:
                    value = value % {"name": self.envname}
                self.config.set(section, option, value)
        self.push(SaveConfig(), target=self.config)

    @handler("verify_environment")
    def _on_verify_environment(self):
        f = open(os.path.join(self.path, "VERSION"), "r")
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
        if not os.path.isabs(logfile):
            logfile = os.path.join(self.path, logfile)
        self.log = Logger(logfile, logname, logtype, loglevel).register(self)
        self.push(EnvironmentLoaded())
