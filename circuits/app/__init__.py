# Package:  app
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Application Components

Contains various components useful for application development and tasks
common to applications.
"""

from .daemon import Daemon
from .dropprivileges import DropPrivileges

__all__ = ("Daemon", "DropPrivileges",)

# flake8: noqa
