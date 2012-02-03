# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event


class WebEvent(Event):

    channels = ("web",)

    success = True
    failure = True


class Request(WebEvent):
    """Request(WebEvent) -> Request WebEvent

    args: request, response
    """


class Response(WebEvent):
    """Response(WebEvent) -> Response WebEvent

    args: request, response
    """


class Stream(WebEvent):
    """Stream(WebEvent) -> Stream WebEvent

    args: request, response
    """
