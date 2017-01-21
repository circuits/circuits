#!/usr/bin/python
from circuits import Component, Event


class simple_event(Event):
    complete = True


class test(Event):

    """test Event"""

    success = True


class Nested3(Component):
    channel = "nested3"

    def test(self):
        """ Updating state. Must be called twice to reach final state."""
        if self.root._state != "Pre final state":
            self.root._state = "Pre final state"
        else:
            self.root._state = "Final state"


class Nested2(Component):
    channel = "nested2"

    def test(self):
        """ Updating state. """
        self.root._state = "New state"
        # State change involves even more components as well.
        self.fire(test(), Nested3.channel)
        self.fire(test(), Nested3.channel)


class Nested1(Component):
    channel = "nested1"

    def test(self):
        """ State change involves other components as well. """
        self.fire(test(), Nested2.channel)


class App(Component):
    channel = "app"
    _simple_event_completed = False
    _state = "Old state"
    _state_when_success = None
    _state_when_complete = None

    def simple_event_complete(self, e, value):
        self._simple_event_completed = True

    def test(self):
        """ Fire the test event that should produce a state change. """
        evt = test()
        evt.complete = True
        evt.complete_channels = [self.channel]
        self.fire(evt, Nested1.channel)

    def test_success(self, e, value):
        """ Test event has been processed, save the achieved state."""
        self._state_when_success = self._state

    def test_complete(self, e, value):
        """
        Test event has been completely processed, save the achieved state.
        """
        self._state_when_complete = self._state


app = App()
Nested1().register(app)
Nested2().register(app)
Nested3().register(app)

while len(app):
    app.flush()


def test_complete_simple():
    """
    Test if complete works for an event without further effects
    """
    app.fire(simple_event())
    while len(app):
        app.flush()

    assert app._simple_event_completed


def test_complete_nested():
    app.fire(test())
    while len(app):
        app.flush()

    assert app._state_when_success == "Old state"
    assert app._state_when_complete == "Final state"
