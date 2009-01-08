#!/usr/bin/env python

import os

from threading import Thread as _Thread
from threading import enumerate as threads

from multiprocessing import Pipe as _Pipe
from multiprocessing import Process as _Process

from multiprocessing import cpu_count as cpus
from multiprocessing import active_children as processes

from circuits.core import listener, Event
from circuits.core import Component as _Component

POLL_INTERVAL = 0.00001
BUFFER_SIZE = 131072

class Read(Event): pass
class Helo(Event): pass
class Error(Event): pass
class Write(Event): pass
class Close(Event): pass

class Thread(_Component):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)

        self.running = False
        self.thread = _Thread(target=self.run, name=self.__class__.__name__)

    def start(self):
        self.running = True
        self.thread.start()

    def run(self):
        pass

    def stop(self):
        self.running = False

class Process(_Component):

    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(*args, **kwargs)

        self.running = False
        self.process = _Process(target=self._run, name=self.__class__.__name__)
        self.parent, self.child = _Pipe()

    def _run(self):
        thread = _Thread(target=self.run)
        thread.start()

        while self.running:
            try:
                self.flush()
                if self.child.poll(POLL_INTERVAL):
                    event = self.child.recv()
                    channel = event.channel
                    target = event.target
                    self.send(event, channel, target)
            except KeyboardInterrupt:
                self.running = False
                break

        thread.join()

    def start(self):
        self.running = True
        self.process.start()

    def run(self):
        pass

    def stop(self):
        self.running = False

    def poll(self, wait=POLL_INTERVAL):
        if self.parent.poll(POLL_INTERVAL):
            event = self.parent.recv()
            channel = event.channel
            target = event.target
            self.send(event, channel, target)
