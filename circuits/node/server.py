# Module:   server
# Date:     ...
# Author:   ...

"""Server

...
"""

import json

from circuits import handler, BaseComponent, Event
from circuits.net.sockets import Close, TCPServer, Write


class Server(BaseComponent):
    """Server

    ...
    """
