# Module:   pools
# Date:     6th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Pools

Thread and Process based "worker" pools.
"""

from time import time
from uuid import uuid4 as uuid
from random import seed, choice
from multiprocessing import cpu_count, Queue

from circuits.core.workers import Task, Worker
from circuits.core import handler, BaseComponent, Event

seed(time())


class Map(Event):
    """Map Event"""


class Pool(BaseComponent):

    channel = "pool"

    def init(self, processes=None, channel=channel):
        self.processes = processes or cpu_count()

        self.workers = []
        self.jobs = Queue(self.processes)

    @handler("started", "registered", channel="*")
    def _on_started_or_registered(self, event, *args):
        if self.workers or (event.name == "registered" and args[0] is not self):
            return

        for i in range(self.processes):
            worker = Worker(self.jobs, channel=uuid()).register(self)
            self.workers.append(worker)

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped_or_unregistered(self, event, *args):
        if not self.workers or (event.name == "registered" and args[0] is not self):
            return

        for worker in self.workers[:]:
            worker.unregister()

        self.workers = []

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        worker = choice(self.workers)
        return self.fire(Task(f, *args, **kwargs), worker.channel)
