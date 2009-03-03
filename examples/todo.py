#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=3 sts=3 ts=3

"""(Example) Todo List

A trivial simple example of using circuits to print a simple
todo list. This example is based off the Trac example of the
same name and demonstrates the same functionality. Circuits'
architecture was partially inspired by that of Trac's architecture
and hence this example.

This example demonstrates:
    * Basic Component creation.
    * Basic Event handling.

This example makes use of:
    * Component
    * Event
    * Manager
"""

from circuits.core import Event, Component, Manager

###
### Events
###

class TodoItem(Event):
    """TodoItem(Event) -> TodoItem Event

    args: name, description
    """

###
### Components
###

class TodoList(Component):

    todos = {}

    def add(self, name, description):
        assert name not in self.todos, "To-do already in list"
        self.todos[name] = description
        self.push(TodoItem(name, description), "added")

class TodoPrinter(Component):

    def added(self, name, description):
        print "TODO: %s" % name
        print "      %s" % description

###
### Main
###

def main():
    manager = Manager()

    todo = TodoList()
    printer = TodoPrinter()

    manager += todo
    manager += printer

    manager.start()

    manager.push(
            TodoItem(
                "Make coffee",
                "Really need to make some coffee"
                ),
            "add")

    manager.push(
            TodoItem(
                "Bug triage",
                "Double-check that all known issues were addressed"
                ),
            "add")

    while manager:
        pass

    manager.stop()

###
### Entry Point
###

if __name__ == "__main__":
    main()
