# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au
from circuits.core.events import LiteralEvent

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event


class WebEvent(Event):

    success = True
    failure = True


class Request(WebEvent):
    """Request(WebEvent) -> Request WebEvent

    args: request, response
    """
    @classmethod
    def create(cls, name, *args, **kwargs):
        """
        All classes derived dynamically from Request are LiteralEvents.
        """
        return LiteralEvent.create(cls, name, *args, **kwargs)


class Response(WebEvent):
    """Response(WebEvent) -> Response WebEvent

    args: request, response
    """


class Stream(WebEvent):
    """Stream(WebEvent) -> Stream WebEvent

    args: request, response
    """
