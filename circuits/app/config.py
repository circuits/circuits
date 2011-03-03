# Module:   config
# Date:     13th August 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Config

Configuration Component. This component uses the  standard
ConfigParser.ConfigParser class and adds support for saving
the configuration to a file.
"""



from configparser import ConfigParser

from circuits import handler, BaseComponent, Event


class ConfigEvent(Event):
    """Config Event"""

    _target =  "config"


class LoadConfig(ConfigEvent):
    """Load Config Event"""

    channel = "load_config"

    end = "config_loaded", ConfigEvent._target


class SaveConfig(ConfigEvent):
    """Save Config Event"""

    channel = "save_config"


class Config(BaseComponent):

    channel = "config"

    def __init__(self, filename, defaults=None, channel=channel):
        super(Config, self).__init__(channel=channel)

        self._config = ConfigParser(defaults=defaults)
        self._filename = filename

    def get(self, section, option, default=None, raw=False, vars=None):
        if self._config.has_option(section, option):
            return self._config.get(section, option, raw, vars)
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

    @handler("load_config")
    def _on_load_config(self):
        self._config.read(self._filename)

    @handler("save_config")
    def _on_save_config(self):
        with open(self._filename, "w") as f:
            self._config.write(f)
