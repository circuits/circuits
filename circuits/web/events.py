# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event

class WebEvent(Event):

    channels = ("web",)


class Request(WebEvent):
    """Request(WebEvent) -> Request WebEvent

    args: request, response
    """

    success = False
    failure = False


class Response(WebEvent):
    """Response(WebEvent) -> Response WebEvent

    args: request, response
    """

    success = True
    failure = True


class Stream(WebEvent):
    """Stream(WebEvent) -> Stream WebEvent

    args: request, response
    """

    success = True
    failure = True

class GenerateResponse(WebEvent):
    """GenerateResponse(WebEvent) -> GenerateResponse WebEvent
    
    args: request
    """


class RequestSuccess(Event):
    pass


class RequestFailure(Event):
    pass
