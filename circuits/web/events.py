# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event

class Request(Event):
    """Request(Event) -> Request Event

    args: request, response
    """

    success = "request_success",
    failure = "request_failure",
    filter = "request_filtered",
    start = "request_started",
    end = "request_completed",

class Response(Event):
    """Response(Event) -> Response Event

    args: request, response
    """

    success = "response_success",
    failure = "response_failure",
    filter = "response_filtered",
    start = "response_started",
    end = "response_completed",

class Stream(Event):
    """Stream(Event) -> Stream Event

    args: request, response
    """

    success = "stream_success",
    failure = "stream_failure",
    filter = "stream_filtered",
    start = "stream_started",
    end = "stream_completed",
