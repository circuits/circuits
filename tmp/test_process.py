#!/usr/bin/python -i

import os
from subprocess import Popen, PIPE

from circuits import Manager, Debugger, Process

class Ping(Process):

    def __init__(self, host):
        super(Ping, self).__init__()

        self.host = host

    def run(self):
        process = Popen("ping %s" % self.host, shell=True, stdout=PIPE, stderr=PIPE,
                    close_fds=True, preexec_fn=os.setsid)
        while self.running:
            out = process.stdout.read(1) # One character at a time
            if out == "" and process.poll() != None:
                self.stop()
            elif out != "":
                self.push(Event(out), "data")
