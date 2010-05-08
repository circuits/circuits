Features
========

Here are just some of the many features circuits comes with:

Component Architecture
----------------------

circuits has a **Component Architecture**.

circuits employs a strong Component Architecture in it's design.
What is a Component Architecture ? In the context of circuits it's
best described as a way of completely decoupling every part of the
system or application. Each Component knows nothing of any of the
other components in the system. This kind of architecture can be
a very powerful tool if used properly.

Other articles on the subject describe the Component Architecture
differently, but nonetheless, here are some good reference and reading
material:

* `Component based Software Engineering <http://en.wikipedia.org/wiki/Software_componentry>`_ (*wikipedia*)
* `Trac's excellent Component Architecture <http://trac.edgewall.org/wiki/TracDev/ComponentArchitecture>`_

The design of circuits is such that the circuits framework containing useful
features in application development, networking and web development is all
implemented as simple and complex components. Functionality of an application
or system is created in components and the interaction of those components.

A good example of this is a simple web application displaying the traditional
"Hello World!" greeting:

:download:`web.py <examples/web.py>`

.. literalinclude:: examples/web.py
   :language: python
   :linenos:

This very simple example demonstrates and makes use of the following set of components::

 * Server
  * TCPServer
   * Select
   * HTTP
  * Dispatcher
   * Root
    * Controller

We won't go into any details about how these components interact with each
other or what their purpose is in such a simple web application, but it should
clearly outline the inherent **Component Architecture** behind circuits.

As a better picture of this, here's a visual graph of this simple example:

.. image:: images/web.png

Event Driven
------------

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

Event Feedback Channels
-----------------------

Within the core of circuits is a feature called **Event Feedback**. This is a
mechanism that ties into any **Event** object allowing feedback to be given
for a number of criteria:

* **success**: An optional channel to use for Event Handler success
* **failure**: An optional channel to use for Event Handler failure
* **filter**: An optional channel to use if an Event is filtered
* **start**: An optional channel to use before an Event starts
* **end**: An optional channel to use when an Event ends

These criterion are specified on the **Event** class as class or instance
attributes and used to trigger an event on the channel specified in the form
of a 2-item tuple: ``(channel, target)``

To demonstrate just one of these **Event Feedback** channels, let's take the :download:`helloworld.py <examples/helloworld.py>` example and modify it a bit to cascade some feedback on the ``Hello`` Event being fired:

.. literalinclude:: examples/helloworld.py
   :language: python
   :linenos:

Replace the ``Hello`` Event in L5-6 with::

   class Hello(Event):
      """Hello Event (with feedback)"""

      end = "goodbye",

Note:
 * Event Feedback channels must be 2-item tuples. The 2nd item (**target**) can be omitted.

Now let's create a new Event Handler for the feedback channel we just defined. Insert the following code above L17::

   def goodbye(self, e, handler, v):
      print "Goodbye World!"
      print "Event:", e
      print "Handler:", handler
      print "Return Value:", v
      raise SystemExit, 0

Let's also modify our orignal ``Hello`` Event Handler so we don't terminate the system with a ``SystemExit`` Exception raised here, instead we'll do this in our Event Feedback's Event Handler (*above*)::

   def hello(self):
      print "Hello World!"

Note:
 * It's important that any Event Handler for Event Feedback channel(s) adhere and define the correct signature (*parameters*). ``end`` feedback for example requires 3 parameters: ``(e, handler, v)``
 * **DO NOT** name the 1st parameter ``event`` as this has a special meaning in any Event Handlers in circuits.
 * See: ... for more information.

When this modified example is run, here's the output you'll expect:

.. code-block:: sh

   $ python source/examples/helloworld.py 
   Hello World!
   Goodbye World!
   Event: <Hello[*:hello] [] {}>
   Handler <bound method App.hello of <App/* (queued=0, channels=3, handlers=3) [R]>>
   Return Value: None

Event Handler Inheritence
-------------------------

Just like in Object Orientated Programming, circuits has this notion of *Inherience*. However in circuits, this means the capability of inheriting Event Handlers from a Base Component. This is done automatically unless the keyword argument *override=True* is given to the Event Handler in the subclassed Component.

For example, let's consider the following simple example:

.. code-block:: python
   :linenos:

   from circuits import handler, Event, Component

   class Hello(Event):
      """Hello Event"""

   class Base(Component):

      def hello(self):
         print "Hello"

   class App(Base):

      def hello(self):
         print "World!"

      def hello_completed(self, e, v, h):
         raise SystemExit, 0

   app = App()
   app.push(Hello())
   app.run()

Runnning this simple example demonstrates *Event Inheritence*:

.. code-block:: sh

   $ python hello.py
   Hello
   World!

It should be obvious here that despite (**from an object orientated programming perspective**) the Base component's hello (**method**) handler being overridden, it's actually inherited. If we wanted to override the Base component's "hello" Event Handler we'd do this:

.. code-block:: python
   :linenos:

   # ...
   from circuits import handler

   class App(Base):

      @handler("hello", override=True)
      def hello(self):
         print "World!"

Runnable Components
-------------------

To makes things a lot easier, circuits removes as much of the unnecessary boiler-plate code necessary to setup a main-loop and run a system. A Manager (*which all components are subclasses of*) has 3 important methods:

* **.start(...)**: Used to start a Component and it's registered structure in either a new thread or process.
* **.stop()**: Used to terminate a running Component.
* **.run(...)**: Used to run a Component in the MainThread (*this blocks*).

Values and Future Values
------------------------

The circuits core framework allows values to be returned from event handlers as well as nested values (*values of other events not yet executed*) and future values (*values not yet computed or that take a while to compite*). A Value object is returned for each call to ``.push(...)`` queing an event into the system.

Example (Value):

.. code-block:: python
   :linenos:

   from circuits import Event, Component
   
   class Test(Event):
      """Test Event"""

   class App(Component):
   
      def test(self, x, y):
         return x + y
   
      def display(self, v):
         print v
         self.stop()
   
   app = App()
   
   x = app.push(Test(4, 7))
   x.onSet = "display",
   
   app.run()

Output:

.. code-block:: sh
   
   $ python test.py 
   11
   
Example (Nested Values):

.. code-block:: python
   :linenos:
   
   from circuits import Event, Component
   
   class Test(Event):
      """Test Event"""
   
   class Eval(Event):
      """Eval Event"""
   
   class App(Component):
   
      def test(self, x, y):
         return self.push(Eval("%d + %d" % (x, y)))
   
      def eval(self, s):
         return eval(s)
   
      def display(self, v):
         print v
         self.stop()
   
   app = App()
   
   x = app.push(Test(4, 7))
   x.onSet = "display",
   
   app.run()

Output:

.. code-block:: sh
   
   $ python test.py 
   11

Example (Future Values):

.. code-block:: python
   :linenos:
   
   from time import sleep
   
   from circuits import future, Event, Component
   
   class Test(Event):
      """Test Event"""
   
   class Eval(Event):
      """Eval Event"""
   
   class App(Component):
   
      def test(self, x, y):
         return self.push(Eval("%d + %d" % (x, y)))
   
      @future()
      def eval(self, s):
         sleep(1)
         return eval(s)
   
      def display(self, v):
         print v
         self.stop()
   
   app = App()
   
   x = app.push(Test(4, 7))
   x.onSet = "display",
   
   app.run()

Output:

.. code-block:: sh
   
   $ python test.py 
   11

Other Features
--------------

 * Pure python implementation. No C extension modules required.
 * Small lightweight core.
 * High performance event framework (See: `Performance <http://bitbucket.org/prologic/circuits/wiki/Performance>`_ on the wiki).
 * Built-in developer tools: ``Debugger, circuits.tools``
 * Application components (*Daemon, Log*).
 * Asynchronous Networking components (*sockets, pollers*).
 * Asynchronous I/O components (*File*, *Serial*).
 * Networking protocol components
 * Small lightweight web framework 
