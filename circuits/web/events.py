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

    success = "request_success", "http"
    failure = "request_failure", "http"
    before = "before_request", "http"
    filter = "request_filtered", "http"
    start = "request_started", "http"
    end = "request_completed", "http"

class Response(Event):
    """Response(Event) -> Response Event

    args: request, response
    """

    success = "response_success", "http"
    failure = "response_failure", "http"
    before = "before_response", "http"
    filter = "response_filtered", "http"
    start = "response_started", "http"
    end = "response_completed", "http"

class Stream(Event):
    """Stream(Event) -> Stream Event

    args: request, response
    """

    success = "stream_success", "http"
    failure = "stream_failure", "http"
    before = "before_stream", "http"
    filter = "stream_filtered", "http"
    start = "stream_started", "http"
    end = "stream_completed", "http"
