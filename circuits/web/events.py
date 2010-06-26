# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event

class WebEvent(Event):

    _target = "web"

class Request(WebEvent):
    """Request(WebEvent) -> Request WebEvent

    args: request, response
    """

    success = "request_success", WebEvent._target
    failure = "request_failure", WebEvent._target
    filter = "request_filtered", WebEvent._target
    start = "request_started", WebEvent._target
    end = "request_completed", WebEvent._target

class Response(WebEvent):
    """Response(WebEvent) -> Response WebEvent

    args: request, response
    """

    success = "response_success", WebEvent._target
    failure = "response_failure", WebEvent._target
    filter = "response_filtered", WebEvent._target
    start = "response_started", WebEvent._target
    end = "response_completed", WebEvent._target

class Stream(WebEvent):
    """Stream(WebEvent) -> Stream WebEvent

    args: request, response
    """

    success = "stream_success", WebEvent._target
    failure = "stream_failure", WebEvent._target
    filter = "stream_filtered", WebEvent._target
    start = "stream_started", WebEvent._target
    end = "stream_completed", WebEvent._target
