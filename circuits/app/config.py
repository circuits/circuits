# Module:   config
# Date:     13th August 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Config

Configuration Component. This component uses the  standard
ConfigParser.ConfigParser class and adds support for saving
the configuration to a file.
"""


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from circuits import handler, BaseComponent, Event


class ConfigEvent(Event):
    """Config Event"""

    channels = ("config",)

    success = True
    failure = True


class Load(ConfigEvent):
    """Load Config Event"""


class Save(ConfigEvent):
    """Save Config Event"""


class Config(BaseComponent):

    channel = "config"

    def __init__(self, filename, defaults=None, channel=channel):
        super(Config, self).__init__(channel=channel)

        self._config = ConfigParser(defaults=defaults)
        self._filename = filename

    @handler("load")
    def load(self):
        self._config.read(self._filename)

    @handler("save")
    def save(self):
        with open(self._filename, "w") as f:
            self._config.write(f)

    def add_section(self, section):
        return self._config.add_section(section)

    def items(self, section, raw=False, vars=None):
        return self._config.items(section, raw=False, vars=None)

    def get(self, section, option, default=None, raw=False, vars=None):
        if self._config.has_option(section, option):
            return self._config.get(section, option, raw=raw, vars=vars)
        else:
            return default

    def getint(self, section, option, default=0):
        if self._config.has_option(section, option):
            return self._config.getint(section, option)
        else:
            return default

    def getfloat(self, section, option, default=0.0):
        if self._config.has_option(section, option):
            return self._config.getfloat(section, option)
        else:
            return default

    def getboolean(self, section, option, default=False):
        if self._config.has_option(section, option):
            return self._config.getboolean(section, option)
        else:
            return default

    def has_section(self, section):
        return self._config.has_section(section)

    def has_option(self, section, option):
        return self._config.has_option(section, option)

    def set(self, section, option, value):
        return self._config.set(section, option, value)
