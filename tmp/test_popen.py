#!/usr/bin/python -i

import os
from subprocess import Popen, PIPE

from circuits import Event, Component
from circuits.io import File, stdout

class Printer(Component):

    def read(self, data):
        self.push(Event(data), "write", "stdout")

p = Popen("ping 127.0.0.1", shell=True, stdout=PIPE, stderr=PIPE,
        close_fds=True)

(File(p.stdout) + Printer() + stdout).run()
