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

        self._workers = []

        for i in range(min):
            self._workers.append(Worker(process=process, channel=str(uuid())))

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        workers = float(len(self._workers))
        tasks = [float(len(worker)) for worker in self._workers]
        total = sum(tasks)
        _avg = total / workers

        assigned = None

        for worker in self._workers:
            if len(worker) < _avg:
                assigned = worker.channel
                return worker.push(Task(f, *args, **kwargs), target=worker)

        if not assigned:
            worker = choice(self._workers)
            assigned = worker.channel
            return worker.push(Task(f, *args, **kwargs), target=worker)
