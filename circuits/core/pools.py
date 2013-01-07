# Module:   pools
# Date:     6th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Pools

Thread and Process based "worker" pools.
"""

from time import time
from uuid import uuid4 as uuid
from random import seed, choice

from circuits.core.workers import Task, Worker
from circuits.core import handler, BaseComponent

seed(time())


class Pool(BaseComponent):

    channel = "pool"

    def __init__(self, min=5, max=10, process=False, channel=channel):
        super(Pool, self).__init__(channel=channel)

        self._min = min
        self._max = max
        self._process_mode = process

        self._workers = []

    @handler("started", "registered", channel="*")
    def _on_started_or_registered(self, *args):
        for i in range(self._min):
            worker = Worker(process=self._process_mode, channel=uuid())
            self._workers.append(worker)

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped_or_unregistered(self, *args):
        for worker in self._workers[:]:
            worker.stop()
        self._workers = []

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        workers = len(self._workers)
        if not workers:
            worker = Worker(process=self._process_mode, channel=uuid())
            self._workers.append(worker)
            return worker.fire(Task(f, *args, **kwargs), worker)

        tasks = [len(worker) for worker in self._workers]
        total = sum(tasks)
        avg = total / workers

        for worker in self._workers:
            if len(worker) < avg:
                return worker.fire(Task(f, *args, **kwargs), worker)

        worker = choice(self._workers)
        return worker.fire(Task(f, *args, **kwargs), worker)
