#!/usr/bin/python -i

from collections import deque
from traceback import format_exc
from functools import update_wrapper

from decorator import decorator

from circuits.tools import graph, inspect
from circuits import Event, Component, Debugger

class Eval(Event): pass
class Error(Event): pass
class Result(Event): pass

class Expression(Component):

        def __init__(self, id, f, *args, **kwargs):
            super(Expression, self).__init__()

            self._id = id
            self._f = f
            self._args = args
            self._kwargs = kwargs

            self._done = False
            self._error = None
            self._result = None

        def __tick__(self):
            try:
                self._result = self._f(*self._args, **self._kwargs)
                self._done = True
                self.push(Result(self._id, self._result), "Result")
            except Exception, e:
                self._error = e
                self.push(Error(self._id, e), "error")
            finally:
                self.unregister()
                self.stop()

        def wait(self):
            while not self._done:
                pass
            return self()

        def __call__(self):
            return self._result if self._done else self

class ExpressionManager(Component):

    def __init__(self, *args, **kwargs):
        super(ExpressionManager, self).__init__(*args, **kwargs)

        self._args = args
        self._kwargs = kwargs

        self._tasks = {}
        self._nextid = -1

    def result(self, id, result):
        self._tasks[id]

    def error(self, id, error):
        self._tasks[id]

    def __call__(self, func):
        return decorator(self.call, func)

    def call(self, func, *args, **kwargs):
        id = self._nextid = self._nextid + 1
        task = Expression(id, func, *args, **kwargs)
        task.start(*self._args, **self._kwargs)
        self._tasks[id] = task
        self += task
        return task

expr = ExpressionManager()# + Debugger()
expr.start()
