#!/usr/bin/env python

from time import sleep, time
from uuid import uuid4 as uuid
from random import seed, choice

from circuits import handler, BaseComponent, Debugger, Event

seed(time())

class NewTask(Event):
    """New Task Event"""

class Task(Event):
    """Task Event"""

class Worker(BaseComponent):

    channel = "worker"

    def __init__(self, channel=channel):
        super(Worker, self).__init__(channel=channel)

        self.start()

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        return f(*args, **kwargs)

class ThreadPool(BaseComponent):

    channel = "pool"

    def __init__(self, min=5, max=10, channel=channel):
        super(ThreadPool, self).__init__(channel=channel)

        self._workers = []

        for i in range(min):
            self._workers.append(Worker(channel=str(uuid())))

    @handler("newtask")
    def _on_new_task(self, f, *args, **kwargs):
        workers = float(len(self._workers))
        tasks = [float(len(worker)) for worker in self._workers]
        total = sum(tasks)
        _min = min(tasks)
        _avg = total / workers
        _max = max(tasks)

        assigned = None

        for worker in self._workers:
            if len(worker) < _avg:
                assigned = worker.channel
                return worker.push(Task(f, *args, **kwargs), target=worker)

        if not assigned:
            worker = choice(self._workers)
            assigned = worker.channel
            return worker.push(Task(f, *args, **kwargs), target=worker)
