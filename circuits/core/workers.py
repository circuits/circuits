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
from multiprocessing import Pool
from Queue import Queue

from .events import Event
from .handlers import handler
from .components import BaseComponent


def processor(queue, results):
    while True:
        job = queue.get()

        if job is None:
            # Poison pill means we should exit
            break

        f, args, kwargs = job

        try:
            results.put(f(*args, **kwargs))
        except Exception as e:
            results.put(e)


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
        self.process = process
        if process:
            self._pool = Pool(1)
        else:
            self.queue = Queue()
            self.results = Queue()

            args = (self.queue, self.results)

            self.processor = Thread(target=processor, args=args)
            self.processor.daemon = True
            self.processor.start()

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped(self, event, *args):
        if event.name == "unregistered" and args[0] is not self:
            return

        self.queue.put(None)
        self.processor.join()

    @handler("task")
    def _on_task(self, event, f, *args, **kwargs):
        if self.process:
            result = self._pool.apply_async(f, args, kwargs)
            while not result.ready():
                yield
            yield result.get()
        else:
            self.queue.put((f, args, kwargs))

            while True:
                try:
                    value = self.results.get_nowait()
                    if isinstance(value, Exception):
                        raise value
                    else:
                        yield value
                    raise StopIteration()
                except Empty:
                    yield

    def resume(self):
        self.results.put((None, None))
