"""Workers

Worker components used to perform "work" in independent threads or
processes. Worker(s) are typically used by a Pool (circuits.core.pools)
to create a pool of workers. Worker(s) are not registered with a Manager
or another Component - instead they are managed by the Pool. If a Worker
is used independently it should not be registered as it causes its
main event handler ``_on_task`` to execute in the other thread blocking it.
"""

from threading import current_thread
from weakref import WeakKeyDictionary
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool as ProcessPool

from .events import Event
from .handlers import handler
from .components import BaseComponent


DEFAULT_WORKERS = 10


class task(Event):

    """task Event

    This Event is used to initiate a new task to be performed by a Worker
    or a Pool of Worker(s).

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

    This Component creates a Worker (either a thread or process) which
    when given a ``Task``, will execute the given function in the task
    in the background in its thread/process.

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
