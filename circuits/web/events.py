# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Events

This module implements the necessary Events needed.
"""

from circuits import Event

class WebEvent(Event):

    _target = "web"

    def __init__(self, *args, **kwargs):
        if 'target' in kwargs:
            self._target = kwargs.pop('target')
        super(WebEvent, self).__init__(*args, **kwargs)


class Request(WebEvent):
    """Request(WebEvent) -> Request WebEvent

    args: request, response
    """
    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.success = "request_success", self._target
        self.failure = "request_failure", self._target
        self.filter = "request_filtered", self._target
        self.start = "request_started", self._target
        self.end = "request_completed", self._target

class Response(WebEvent):
    """Response(WebEvent) -> Response WebEvent

    args: request, response
    """
    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.success = "response_success", self._target
        self.failure = "response_failure", self._target
        self.filter = "response_filtered", self._target
        self.start = "response_started", self._target
        self.end = "response_completed", self._target

class Stream(WebEvent):
    """Stream(WebEvent) -> Stream WebEvent

    args: request, response
    """
    def __init__(self, *args, **kwargs):
        super(Stream, self).__init__(*args, **kwargs)
        self.success = "stream_success", self._target
        self.failure = "stream_failure", self._target
        self.filter = "stream_filtered", self._target
        self.start = "stream_started", self._target
        self.end = "stream_completed", self._target
