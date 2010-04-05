Event Driven
============

circuits is **Event Driven**.

circuits helps facilitate "Event Driven" programming.
What is Event Driven Programming ? It's a technique of programming
whereby events are scheduled into some kind of a queue
and handled by event handlers. Some really good
references and reading material can be found here:
* `Event Driven Programming <http://en.wikipedia.org/wiki/Event-driven_programming>`_ (*wikipedia*)
* `Event Driven Programming. Introduction, Tutorial and History <http://eventdrivenpgm.sourceforge.net/>`_ (*sourceforge*)

in circuits, this means that everything you do in a circuits-based
application or system is the reaction to or exposure of some kind of
"Event". Components communicate with one another by passing back and forth
events on various channels. Each Component itself also defines it's own
channel (*sub channel*) which allows two or more components with similar
events to co-exist without interfering with each other.

To demonstrate some of these concepts, let's look at what an **Event** is:

Let's import the base Event class:

>>> from circuits import Event

Now let's create a simple Event called ``Test``:

>>> class Test(Event):
...     """Test Event"""
... 

Let's create an instance of this new ``Test`` Event and test some properties on it:

>>> e = Test()
>>> e
<Test[] [] {}>
>>> e.channel
>>> e.args
[]
>>> e.kwargs
{}

Note:
 * Test has no channel defined or set yet.
 * Test has no arguments (**.args**) or keyword arguments (**.kwargs**).

Now let's push/fire this Event and see what happens. We first need to import
and use a Manager:

>>> from circuits import Manager
>>> m = Manager()

Let's push/fire the Event:

>>> m.push(e)
<Value () result: False errors: False for <Test[*:test] [] {}>

Note:
 * An object is returned called a Value. See: :doc:`values`

Let's check the same properties on our Event object/instance now after it's been pushed/fired:

>>> e
<Test[*:test] [] {}>
>>> e.channel
('*', 'test')

Note:
 * The channel has been set/defined as: ``("*", "test")`` (*default behavior*).
