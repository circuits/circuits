# Module:   config
# Date:     13th August 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Config

Configuration Component. This component uses the  standard
ConfigParser.ConfigParser class and adds support for saving
the configuration to a file.
"""


from ConfigParser import ConfigParser

from circuits import handler, Event, Component


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


class Config(Component, ConfigParser):

    channel = "config"

    def __init__(self, filename, defaults=None):
        Component.__init__(self)
        ConfigParser.__init__(self, defaults=defaults)

        self.filename = filename

    def get(self, section, option, default=None, raw=False, vars=None):
        if self.has_option(section, option):
            return super(Config, self).get(section, option, raw, vars)
        else:
            return default

    def getint(self, section, option, default=0):
        if self.has_option(section, option):
            return super(Config, self).getint(section, option)
        else:
            return default

    def getfloat(self, section, option, default=0.0):
        if self.has_option(section, option):
            return super(Config, self).getfloat(section, option)
        else:
            return default

    def getboolean(self, section, option, default=False):
        if self.has_option(section, option):
            return super(Config, self).getboolean(section, option)
        else:
            return default

    @handler("load_config")
    def _on_load_config(self):
        self.read(self.filename)

    @handler("save_config")
    def _on_save_config(self):
        f = open(self.filename, "w")
        self.write(f)
        f.close()
