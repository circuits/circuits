# Module:   pools
# Date:     6th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Pools

Thread and Process based "worker" pools.
"""

from time import time
from random import seed, choice

from circuits.core.workers import Task, Worker
from circuits.core import handler, BaseComponent

seed(time())


class Pool(BaseComponent):

    channel = "pool"

    def __init__(self, min=5, max=10, processes=False, channel=channel):
        super(Pool, self).__init__(channel=channel)

        self._min = min
        self._max = max
        self._processes = processes

        self._workers = []

    @handler("started", channel="*")
    def _on_started(self, *args):
        for i in range(self._min):
            worker = Worker(process=self._processes,
                            channel=self.channel + str(i + 1))
            self._workers.append(worker)

    @handler("stopped", channel="*")
    def _on_stopped(self, *args):
        for worker in self._workers[:]:
            worker.stop()
        self._workers = []

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        workers = len(self._workers)
        if not workers:
            worker = Worker(process=self._processes)
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
