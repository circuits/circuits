#!/usr/bin/python -i

from circuits import Event, Component
from circuits.core.debugger import Debugger

state = "Old state"
state_when_success = None
state_when_complete = None

class Test(Event):
    """Test Event"""
    success = True

class Nested2(Component):
    channel = "nested2"

    def test(self):
        """ Updating state. """
        global state
        state = "New state"
        
class Nested1(Component):
    channel = "nested1"

    def test(self):
        """ State change involves other components as well. """
        self.fire(Test(), Nested2.channel)
        
class App(Component):
    channel = "app"

    def test(self):
        """ Fire the test event that should produce a state change. """
        evt = Test()
        evt.complete = True
        evt.complete_channels = [self.channel]
        self.fire(evt, Nested1.channel)
        
    def test_success(self, e, value):
        """ Test event has been processed, save the achieved state."""
        global state_when_success, state
        state_when_success = state

    def test_complete(self, e, value):
        """ Test event has been completely processed, 
            save the achieved state."""
        global state_when_complete, state
        state_when_complete = state

app = App()
Nested1().register(app)
Nested2().register(app)
Debugger().register(app)

while app: app.flush()

def test_state():
    app.fire(Test()) # trigger processing
    while app: app.flush()
    assert state_when_success == "Old state"
    assert state_when_complete == "New state"

