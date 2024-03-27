"""Help Tasks"""

from fabric import state
from fabric.api import task
from fabric.task_utils import crawl
from fabric.tasks import Task


@task(default=True)
def help(name=None):
    """
    Display help for a given task

    Options:
        name    - The task to display help on.

    To display a list of available tasks type:

        $ fab -l

    To display help on a specific task type:

        $ fab help:<name>
    """
    if name is None:
        name = 'help'

    task = crawl(name, state.commands)
    if isinstance(task, Task):
        doc = getattr(task, '__doc__', None)
        if doc is not None:
            print(f'Help on {name:s}:')
            print()
            print(doc)
        else:
            print(f'No help available for {name:s}')
    else:
        print(f'No such task {name:s}')
        print('For a list of tasks type: fab -l')
