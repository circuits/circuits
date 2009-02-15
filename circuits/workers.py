#!/usr/bin/env python

from threading import Thread as _Thread
from threading import enumerate as threads

from multiprocessing import Pipe as _Pipe
from multiprocessing import Value as _Value
from multiprocessing import Process as _Process

from multiprocessing import cpu_count as cpus
from multiprocessing import active_children as processes

from circuits.core import Component as _Component

POLL_INTERVAL = 0.00001

class Thread(_Component):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)

        self.running = False
        self.thread = _Thread(target=self.run)

    def start(self):
        self.running = True
        self.thread.start()

    def run(self):
        pass

    def stop(self):
        self.running = False
        return self.thread.join()

    def isAlive(self):
        return self.running and self.thread.isAlive()

class Process(_Component):

    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(*args, **kwargs)

        self.running = _Value("b", False)
        self.process = _Process(target=self._run, args=(self.run, self.running,))
        self.parent, self.child = _Pipe()

    def _run(self, fn, running):
        thread = _Thread(target=fn)
        thread.start()

        try:
            while running.value:
                try:
                    self.flush()
                    if self.child.poll(POLL_INTERVAL):
                        event = self.child.recv()
                        channel = event.channel
                        target = event.target
                        self.send(event, channel, target)
                except SystemExit:
                    running.acquire()
                    running.value = False
                    running.release()
                    break
                except KeyboardInterrupt:
                    running.acquire()
                    running.value = False
                    running.release()
                    break
        finally:
            running.acquire()
            running.value = False
            running.release()
            thread.join()
            self.flush()

    def start(self):
        self.running.acquire()
        self.running.value = True
        self.running.release()
        self.process.start()

    def run(self):
        pass

    def stop(self):
        self.running.acquire()
        self.running.value = False
        self.running.release()

    def isAlive(self):
        return self.running.value

    def poll(self, wait=POLL_INTERVAL):
        if self.parent.poll(POLL_INTERVAL):
            event = self.parent.recv()
            channel = event.channel
            target = event.target
            self.send(event, channel, target)
