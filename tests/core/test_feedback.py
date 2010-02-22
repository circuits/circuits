# Module:   test_feedback
# Date:     11th February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Feedback Channels Tests"""

import py

from circuits import handler, Event, Component

class Test(Event):
    """Test Event"""

    success = ("test_successful",)
    failure = ("test_failed",)
    filter = ("test_filtered",)
    start = ("test_started",)
    end = ("test_ended",)

class App(Component):

    def __init__(self):
        super(App, self).__init__()

        self.states = []
        self.events = []
        self.values = []
        self.errors = []
        self.handlers = []

    @handler(filter=True)
    def event(self, event, *args, **kwargs):
        """Global Event Handler (filter)"""

        if kwargs.get("filter", False):
            return True

    def test(self, error=False):
        if error:
            raise Exception("Hello World!")

        return "Hello World!"

    def test_successful(self, evt, handler, retval):
        self.states.append("success")
        self.events.append(evt)
        self.handlers.append(handler)
        self.values.append(retval)

    def test_failed(self, evt, handler, error):
        self.states.append("failure")
        self.events.append(evt)
        self.handlers.append(handler)
        self.errors.append(error)

    def test_filtered(self, evt, handler, retval):
        self.states.append("filter")
        self.events.append(evt)
        self.handlers.append(handler)
        self.values.append(retval)

    def test_started(self, evt):
        self.states.append("start")
        self.events.append(evt)

    def test_ended(self, evt, handler, retval):
        self.states.append("end")
        self.events.append(evt)
        self.handlers.append(handler)
        self.values.append(retval)

def reraise(e):
    raise e

def test():
    app = App()
    while app:
        app.flush()

    e = Test()
    x = app.push(e)

    app.flush()

    # "start" feedback
    assert app.states[-1:][0] == "start"
    assert app.events[-1:][0] == e
    assert not app.values
    assert not app.errors
    assert not app.handlers

    # The Event
    s = x.value
    assert s == "Hello World!"

    app.flush()

    # "success", "failure" or "filter" and "end" feedback
    assert app.states[-2:][0] == "success"
    assert app.events[-2:][0] == e
    assert app.values[-2:][0] == "Hello World!"
    assert not app.errors
    assert app.handlers[-2:][0] == app.test

    assert app.states[-1:][0] == "end"
    assert app.events[-1:][0] == e
    assert app.values[-1:][0] == "Hello World!"
    assert not app.errors
    assert app.handlers[-1:][0] == app.test

def test_failure():
    app = App()
    while app:
        app.flush()

    e = Test(error=True)
    x = app.push(e)

    app.flush()

    # "start" feedback
    assert app.states[-1:][0] == "start"
    assert app.events[-1:][0] == e
    assert not app.values
    assert not app.errors
    assert not app.handlers

    # The Event
    py.test.raises(Exception, lambda x: reraise(x[1]), x.value)

    app.flush()

    # "success", "failure" or "filter" and "end" feedback
    assert app.states[-2:][0] == "failure"
    assert app.events[-2:][0] == e
    assert app.values
    assert app.values[-2:][0] == None
    assert app.errors
    py.test.raises(Exception, lambda x: reraise(x[1]), app.errors[-2:][0])
    assert app.handlers[-2:][0] == app.test

    assert app.states[-1:][0] == "end"
    assert app.events[-1:][0] == e
    assert app.values
    assert app.values[-1:][0] == None
    assert app.errors
    py.test.raises(Exception, lambda x: reraise(x[1]), app.errors[-1:][0])
    assert app.handlers[-1:][0] == app.test

def test_filter():
    app = App()
    while app:
        app.flush()

    e = Test(filter=True)
    x = app.push(e)

    app.flush()

    # "start" feedback
    assert app.states[-1:][0] == "start"
    assert app.events[-1:][0] == e
    assert not app.values
    assert not app.errors
    assert not app.handlers

    # The Event
    s = x.value
    assert type(s) is bool
    assert s == True

    app.flush()

    # "success", "failure" or "filter" and "end" feedback
    assert app.states[-1:][0] == "filter"
    assert app.events[-1:][0] == e
    assert app.values
    assert app.values[-1:][0] == True
    assert not app.errors
    assert app.handlers[-1:][0] == app.event

    # No 'end' events for filtered events.
