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

from .events import Event
from .utils import findroot
from .manager import Manager
from .handlers import handler
from .components import BaseComponent


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

    def __init__(self, process=False, channel=channel):
        super(Worker, self).__init__(channel=channel)

        if process:
            self.start(link=self, process=True)
            self.start()
        else:
            self.start()

    @handler("task")
    def _on_task(self, f, *args, **kwargs):
        return f(*args, **kwargs)
