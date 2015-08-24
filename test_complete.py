#!/usr/bin/env python


from __future__ import print_function

from time import sleep


import circuits
from circuits import Component, task, Event, Debugger, Worker


class event_a(Event):
    pass


class event_b(Event):
    pass


global_event_b_done = False


class C1(Component):
    worker = Worker()

    def event_a(self):
        print("C1")
        e = task(self._do_task)
        self.fire(e)

    def _do_task(self):
        sleep(2)
        print("Done")
        self.fire(event_b())


class C2(Component):
    def event_b(self):
        print("C2")
        global global_event_b_done
        global_event_b_done = True


class App(Component):
    c1 = C1()
    c2 = C2()

    def started(self, *_):
        event = event_a()
        event.complete = True
        yield self.call(event)

    def event_a_complete(self, *_):
        # global global_event_b_done
        # assert global_event_b_done
        print("Completed")


def main():
    print("circuits {0}".format(circuits.__version__))
    (App() + Debugger()).run()


if __name__ == '__main__':
    main()
