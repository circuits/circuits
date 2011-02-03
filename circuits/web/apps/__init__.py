# Package:  apps
# Date:     3rd February 2011
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Apps

This package contains self-contained small packaged apps that come shipped
with circuits.web that can be used within a circuits.web application.
"""

from circuits.web.apps.webconsole import WebConsole
from circuits.web.apps.memorymonitor import MemoryMonitor

__all__ = (
        "WebConsole",
        "MemoryMonitor",
)
