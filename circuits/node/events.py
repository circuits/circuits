# Module:   events
# Date:     ...
# Author:   ...

"""Events

...
"""

from circuits import Event


class Packet(Event):
    """Packet Event"""


class Remote(Event):
    """Remote Event

    ...
    """

    def __init__(self, event, node, *channels):
        super(Remote, self).__init__(event, node, *channels)
