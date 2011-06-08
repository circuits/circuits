# Module:   startup
# Date:     21st March 2011
# Author:   James Mills, jamesmills at comops dot com dot au

"""Startup Component

This module implements a ``Startup`` Component that create a unified
way of creating, managing and running an application in conjunction with
an environment (``circuits.app.env``). The ``Startup`` Component provides
five verbs that can be passed as command-line arguments:
- start   -- Start the application
- stop    -- Stop the application
- init    -- Create the application environment
- rehash  -- Reload the application's environment
- upgrade -- Upgrade the application's environment
"""

import os
import errno
from time import sleep
from signal import SIGINT, SIGHUP, SIGTERM

from circuits import handler, Event, BaseComponent

from .daemon import Daemon
from .env import Environment
from .env import Create, Load, Upgrade


class Error(Exception):
    """Error Exception"""


class Command(Event):
    """Command Event"""


class Terminate(Event):
    """Terminate Event"""


class Startup(BaseComponent):

    channel = "startup"

    def __init__(self, path, opts, command, env=Environment,
            channel=channel):
        super(Startup, self).__init__(channel=channel)

        self.path = path
        self.opts = opts
        self.command = command

        self.env = env(path).register(self)

    def _getpid(self):
        with open(self.config.get("general", "pidfile"), "r") as f:
            return int(f.read().strip())

    def __tick__(self):
        if not self.command == "start" and not self:
            self.stop()

    @handler("signal", channel="*")
    def _on_signal(self, signal, track):
        if signal in (SIGINT, SIGTERM):
            self.fire(Terminate())

    @handler("environment_loaded", channel="env")
    def _on_environment_loaded(self, *args):
        self.fire(Command(), self.command, self)

    @handler("started")
    def _on_started(self, component):
        if not self.command == "init":
            if not os.path.exists(self.env.path):
                raise Error("Environment does not exist!")
            else:
                self.fire(LoadEnvironment(), self.env)
        else:
            if os.path.exists(self.env.path):
                raise Error("Environment already exists!")
            else:
                self.fire(Command(), self.command, self)

    @handler("start")
    def _on_start(self):
        if self.opts.daemon:
            pidfile = self.env.config.get("general", "pidfile", "app.pid")
            Daemon(pidfile, self.env.path).register(self)

    @handler("stop")
    def _on_stop(self):
        pid = self._getpid()

        try:
            os.kill(pid, SIGTERM)
            os.waitpid(pid, os.WTERMSIG(0))
        except OSError as e:
            if not e.args[0] == errno.ECHILD:
                raise

    @handler("restart")
    def _on_restart(self):
        self.fire(Command(), "stop", self.channel)
        sleep(1)
        self.fire(Command(), "start", self.channel)

    @handler("rehash")
    def _on_rehash(self):
        pid = self._getpid()

        os.kill(pid, SIGHUP)

    @handler("init")
    def _on_init(self):
        self.fire(CreateEnvironment(), self.env)

    @handler("upgrade")
    def _on_upgrade(self):
        self.fire(UpgradeEnvironment(), self.env)
