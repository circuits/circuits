"""Workers

Worker is a component used to perform "work" in independent threads or
processes. Simply create an instance of Worker() with either `process=True`
to create a pool of workers using sub-processes for CPU-bound work or `False`
(the default) for a thread pool of workers for I/O bound work.

Then fire `task()` events with a function and *args and **kwargs to pass
to the function when called from within the workers.
"""
from multiprocessing import Pool as ProcessPool, cpu_count
from multiprocessing.pool import ThreadPool
from threading import current_thread
from weakref import WeakKeyDictionary

from .components import BaseComponent
from .events import Event
from .handlers import handler

DEFAULT_WORKERS = 10


class task(Event):

    """task Event

    This Event is used to initiate a new task to be performed by a Worker

    :param f: The function to be executed.
    :type  f: function

    :param args: Arguments to pass to the function
    :type  args: tuple

    :param kwargs: Keyword Arguments to pass to the function
    :type  kwargs: dict
    """

    success = True
    failure = True

    def __init__(self, f, *args, **kwargs):
        "x.__init__(...) initializes x; see x.__class__.__doc__ for signature"

        super(task, self).__init__(f, *args, **kwargs)


class Worker(BaseComponent):

    """A thread/process Worker Component

    This Component creates a pool of workers (either a thread or process)
    and executures the supplied function from a `task()` event passing
    supplied arguments and keyword-arguments to the function.

    A `task_success` event is fired upon successful execution of the function
    and `task_failure` if it failed and threw an exception. The `task()` event
    can also be "waited" upon by using the `.call()` and `.wait()` primitives.

    :param process: True to start this Worker as a process (Thread otherwise)
    :type process: bool
    """

    channel = "worker"

    def init(self, process=False, workers=None, channel=channel):
        if not hasattr(current_thread(), "_children"):
            current_thread()._children = WeakKeyDictionary()

        self.workers = workers or (cpu_count() if process else DEFAULT_WORKERS)
        Pool = ProcessPool if process else ThreadPool
        self.pool = Pool(self.workers)

    @handler("stopped", "unregistered", channel="*")
    def _on_stopped(self, event, *args):
        if event.name == "unregistered" and args[0] is not self:
            return

        self.pool.close()
        self.pool.join()

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        result = self.pool.apply_async(f, args, kwargs)
        while not result.ready():
            yield
        yield result.get()
