# Module:   client
# Date:     ...
# Author:   ...

"""Client

...
"""

import json

from circuits import handler, BaseComponent, Event
from circuits.net.sockets import Close, Connect, TCPClient, Write


class Client(BaseComponent):
    """Client

    ...
    """
