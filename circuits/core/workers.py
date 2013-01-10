# Module:   workers
# Date:     6th February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Workers

Worker components used to perform "work" in independent threads or
processes. Worker(s) are typically used by a Pool (circuits.core.pools)
to create a pool of workers. Worker(s) are not registered with a Manager
or another Component - instead they are managed by the Pool. If a Worker
is used independently it should not be registered as it causes its
main event handler ``_on_task`` to execute in the other thread blocking it.
"""

from Queue import Empty
from threading import Thread
from multiprocessing import Process
from Queue import Queue as ThreadQueue
from multiprocessing import Queue as ProcessQueue

from .events import Event
from .handlers import handler
from .components import BaseComponent


def processor(queue, results):
    while True:
        job = queue.get()

        if job is None:
            # Poison pill means we should exit
            break

        id, f, args, kwargs = job

        try:
            results.put((id, f(*args, **kwargs)))
        except Exception as e:
            results.put((id, e))


class Task(Event):
    """Task Event

    This Event is used to initiate a new task to be performed by a Worker
    or a Pool of Worker(s).

    :param f: The function to be executed.
    :type  f: function

    :param args: Arguments to pass to the function
    :type  args: tuple

    :param kwargs: Keyword Arguments to pass to the function
    :type  kwargs: dict
    """

    def __init__(self, f, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(Task, self).__init__(f, *args, **kwargs)


class Worker(BaseComponent):
    """A thread/process Worker Component

    This Component creates a Worker (either a thread or process) which
    when given a ``Task``, will execute the given function in the task
    in the background in its thread/process.

    :param process: True to start this Worker as a process (Thread otherwise)
    :type process: bool
    """

    channel = "worker"

    def init(self, process=False, queue=None, channel=channel):
        Queue = ProcessQueue if process else ThreadQueue
        Processor = Process if process else Thread

        self.queue = queue or Queue()
        self.results = Queue()
        self.values = {}
        self.id = 0

        args = (self.queue, self.results)

        self.processor = Processor(target=processor, args=args)
        self.processor.daemon = True
        self.processor.start()

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped(self, event, *args):
        if event.name == "unregistered" and args[0] is not self:
            return

        self.queue.put(None)
        self.processor.join()

    @handler("generate_events")
    def _on_generate_events(self, event):
        try:
            timeout = event.time_left

            if timeout > 0:
                self.root.needs_resume = self.resume
                id, value = self.results.get(True, timeout)
                self.root.needs_resume = None
            else:
                id, value = self.results.get_nowait()

            if id is not None:
                self.values[id].errors = isinstance(value, Exception)
                self.values[id].result = True
                self.values[id].value = value
        except Empty:
            return

    @handler("task")
    def _on_task(self, event, f, *args, **kwargs):
        self.id += 1
        value = event.value
        self.values[self.id] = value

        self.queue.put((self.id, f, args, kwargs))

        while not value.result:
            yield

        if isinstance(value.value, Exception):
            raise value.value
        else:
            yield value.value

    def resume(self):
        self.results.put((None, None))
