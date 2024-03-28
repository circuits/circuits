#!/usr/bin/env python

from time import sleep

from circuits import Component, Debugger, Event, Timer, Worker, task


def factorial(n):
    x = 1
    for i in range(1, (n + 1)):
        x = x * (i + 1)
        sleep(1)  # deliberate!
    return x


class App(Component):
    def init(self, *args, **kwargs):
        Worker(process=True).register(self)

    def foo(self):
        print('Foo!')

    def started(self, component):
        self.fire(task(factorial, 3))  # async
        self.fire(task(factorial, 5))  # async
        self.fire(task(factorial, 7))  # async
        self.fire(task(factorial, 10))  # async
        self.fire(task(factorial, 11))  # async
        self.fire(task(factorial, 11))  # async
        self.fire(task(factorial, 12))  # async
        self.fire(task(factorial, 14))  # async
        Timer(1, Event.create('foo'), persist=True).register(self)

    def task_success(self, function_called, factorial_result):
        _func, argument = function_called
        print(f'factorial({argument!s}) = {factorial_result:d}')
        # Stop after the last and longest running task
        if argument == 14:
            self.stop()


if __name__ == '__main__':
    app = App()
    Debugger().register(app)
    app.run()
