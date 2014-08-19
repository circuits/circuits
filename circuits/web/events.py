# Module:   events
# Date:     3rd February 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Events

This module implements the necessary Events needed.
"""


from circuits import Event


class request(Event):
    """request(Event) -> request Event

    args: request, response
    """

    success = True
    failure = True
    complete = True


class response(Event):
    """response(Event) -> response Event

    args: request, response
    """

    success = True
    failure = True
    complete = True


class stream(Event):
    """stream(Event) -> stream Event

    args: request, response
    """

    success = True
    failure = True
    complete = True


class terminate(Event):
    """terminate Event"""
