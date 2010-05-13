Tutorial
========

Overview
--------

Welcome to the circuits tutorial. Let's get a few things out of the way...

As mentioned in the README (*included in the circuits distribution*) and in
the introduction to this documentation, circuits is:

a **Lightweight** **Event** driven **Framework** for the
`Python Programming Language <http://www.python.org/>`_ with a
strong **Component** Architecture.

There is a certain style to programming with the circuits framework. It might
be a little foreign at first, but once you get the hang of it, it's actually
fairly straight forward.

In circuits, you implement a functional system by implementing smaller
functional componnets that interact together to produce more complex
behavior. For example, Component A might be responsible for doing a set
of tasks, while Component B responsible for another set of tasks. The
two components might occasionally communicate some information (*by passing
messages/events*) to cooperate accomplishing bigger tasks.

The three most important things in circuits are;

* Events
* Components
* Interaction between components

Oh and by the way... In case you're confused, circuits is completely
asynchroneous in nature. This means things are performed in a highly
concurrent way and circuits encourages concurrent and distributed
programming.

Without further ado, let's start introducing concepts in circuits...

Events
------

In circuits, information is passed around components in the form of events
(*or messages*). circuits defines an Event class which is used to create an
actual Event object which holds Event data and properties about that event.

The Event object is what is passed around a system of components and also
what is passed to other processes or remote nodes (*by using a Bridge*).

Creating an event
~~~~~~~~~~~~~~~~~

To create an event, simply create an instance of the Event class and pass
any required data to it's constructor. For example:

.. code-block:: python
   
   e = Event(1, 2, 3, op="add")

This creates an Event object contianing two pieces of data:

* A list containing the numbers: 1, 2, 3
* A string "add" whoose key is ``op`` (*stored as kwargs*).

The Event class's constructor is defined as:

.. code-block:: python
   
   class Event(object):

      def __init__(self, *args, **kwargs):
         ...
   

Event Handlers
--------------

Components
----------

Values
------

Futures
-------

Asynchronous I/O
----------------

Debugging
---------

Tools
-----

