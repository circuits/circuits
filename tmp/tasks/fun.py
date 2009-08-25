#!/usr/bin/python -i

import time
from collections import deque
from traceback import format_exc

from greenlet import greenlet, getcurrent, GreenletExit

from circuits.tools import graph, inspect
from circuits import Event, Component, Debugger

class SwitchedTask(Event): pass
class NewTask(Event): pass
class Asleep(Event): pass
class Awake(Event): pass

class Task(Component):

    channel = None

    def __init__(self, scheduler, channel=channel):
        super(Task, self).__init__(channel=channel)

        self.scheduler = scheduler
        self.register(scheduler)

    def __call__(self, f):
        def _decorator(*args, **kwargs):
            self.push(NewTask(f, *args, **kwargs), "newtask")
        return _decorator

class Sleep(Task):

    channel = None

    def __init__(self, scheduler, channel=channel):
        super(Sleep, self).__init__(scheduler, channel=channel)

        self.sleeping = deque()

    def __tick__(self):
        ctime = time.time()
        sleeping = self.sleeping
        self.sleeping = deque()
        while sleeping:
            task, wtime = sleeping.pop()
            if wtime < ctime:
                self.push(Awake(task), "awake")
                task.switch()
            else:
                self.sleeping.append((task, wtime))

    def __call__(self, delta):
        task = getcurrent()
        ctime = time.time()
        wtime = ctime + delta
        self.sleeping.append((task, wtime))
        self.push(Asleep(task), "asleep")
        self.scheduler.switch()

class Scheduler(Component):

    channel = None

    def __init__(self, channel=channel):
        super(Scheduler, self).__init__(channel=channel)

        self.queue = list()

    def __tick__(self):
        self.g = greenlet(self.step)
        self.switch()

    def newtask(self, f, *args, **kwargs):
        def task():
            f(*args, **kwargs)
            try:
                getcurrent().parent.switch()
            except GreenletExit:
                pass
        self.queue.append(greenlet(task))

    def step(self):
        q = self.queue
        self.queue = deque()
        while q:
            task = q.pop()
            task.switch()

    def switch(self, task=None):
        if task:
            return task.switch()
        else:
            return self.g.switch()

    def unswitch(self):
        return self.g.parent.switch()

scheduler = Scheduler() + Debugger()
sleep = Sleep(scheduler)
task = Task(scheduler)
