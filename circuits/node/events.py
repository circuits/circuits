# Module:   events
# Date:     ...
# Author:   ...

"""Events

...
"""

from circuits import Event


class packet(Event):
    """packet Event"""


class remote(Event):
    """remote Event

    ...
    """

    def __init__(self, event, node, channel=None):
        super(remote, self).__init__(event, node, channel=None)
