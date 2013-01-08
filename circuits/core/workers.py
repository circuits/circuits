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
from multiprocessing import Process, Queue

from .events import Event
from .handlers import handler
from .components import BaseComponent


class Processor(Process):

    def __init__(self, queue, results):
        super(Processor, self).__init__()

        self.queue = queue
        self.results = results

    def run(self):
        while True:
            job = self.queue.get()

            if job is None:
                # Poison pill means we should exit
                break

            f, args, kwargs = job

            try:
                self.results.put(f(*args, **kwargs))
            except Exception as e:
                self.results.put(e)


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

    def init(self, queue=None, channel=channel):
        self.queue = queue or Queue(1)
        self.results = Queue(1)

        self.processor = Processor(self.queue, self.results)
        self.processor.start()

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped(self, event, *args):
        if event.name == "unregistered" and args[0] is not self:
            return

        self.queue.put(None)

    @handler("task")
    def _on_task(self, event, f, *args, **kwargs):
        self.queue.put((f, args, kwargs))

        while True:
            try:
                value = self.results.get_nowait()
                if isinstance(value, Exception):
                    print("...")
                    raise value
                else:
                    yield value
                raise StopIteration()
            except Empty:
                yield
