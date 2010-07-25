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
functional components that interact together to produce more complex
behavior. For example, Component A might be responsible for doing a set
of tasks, while Component B is responsible for another set of tasks. The
two components might occasionally communicate some information (*by passing
messages/events*) to cooperate accomplishing bigger tasks. Designing your
system/application this way encourages a decoupled design and components
in circuits are designed to help accomplish this.

This is called the **Component Architecture**.

The three most important things in circuits are;

* Events
* Components
* Interaction between components

Oh and by the way... In case you're confused, circuits is completely
asynchronous in nature. This means things are performed in a highly
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
any required data to its constructor. For example:

.. code-block:: python

   e = Event(1, 2, 3, op="add")

This creates an Event object containing two pieces of data:

* A list containing the numbers: 1, 2, 3
* A string "add" whoose key is ``op`` (*stored as kwargs*).

The Event class's constructor is defined as:

.. code-block:: python

   class Event(object):

      def __init__(self, ``*args, **kwargs``):
         ...

**Note**: Normally you would subclass ``Event`` and create your own classes of
          events with appropriate docstrings describing what the event is and
          what it's used for. You may even create constraints in the args and
          keyword args that can be passed to it during initialization.

Using an Event
~~~~~~~~~~~~~~

Once an Event object is created, you can push/fire it into a system by calling
the ``.push(...)`` or ``.fire(...)`` method on any Component in the system or
Manager. For example:

.. code-block:: python
   :linenos:

   from circuits import Event, Manager

   m = Manager()
   e = Event("foo")
   m.push(e)
   m.push(Event("bar"))

Now this doesn't do anything very useful by itself, but we'll get to more
useful things later...

Event Handlers
--------------

In order to do useful things with events and components we need a way to
create **Event Handlers** that react to events. In circuits there are two
types of handlers: **Listeners** and **Filters**.

A Listener is an Event Handler that simply "listens" for an Event while a
Filter is an Event Handler with a higher priority than Listeners and is
capable of filtering the Event from other handlers.

To create an Event Handler (*a Listener*) simply use the ``handler(...)``
decorator on a Component:

.. code-block:: python
   :linenos:

   from circuits import handler, Component

   class System(Component):

      @handler("hello")
      def onHello(self):
         print "Hello World!"

This will create a Component called ``System`` that defines an Event Handler
that listens to the channel "hello".

**Note:**
 * The Component automatically defines methods to be Event Handlers that listen
   to a channel that is the name of the method. If a Component defines a method
   called ``foo``, an an Event Handler will be created that listens to the
   channel "foo".

Components
----------

What makes circuits unique in its own way is its **Component Architecture**.
The "circuits way" (tm) is to create components that represent different
functional parts of your system or application. One of the key concepts
is to create more complex components from simpler components. This is a bit
different to subclassing and using multiple inheritance in OOP
(*Object Orientated Programming*). Components are registered to one another
in a directed graph/structure giving a system/application great flexibility.
Components can be registered and unregistered at run-time and even modified.

A Component is also a Manager and every Component can be run independently.

There are three ways in which you can start a Component/Manager:

* ``.run()``: running in the main thread.
* ``.start()``: running in a new separate thread.
* ``.start(process=True)``: running in a new separate process.

Let's look at a few common things that components are used for...

Defining a new Component
~~~~~~~~~~~~~~~~~~~~~~~~

To define a new (*more complex*) Component, simply create a new class that
derives from ``Component``:

.. code-block:: python
   :linenos:

   from circuits import Component

   class System(Component):
      """My System Component"""

Registering Components
~~~~~~~~~~~~~~~~~~~~~~

Components are registered to one another or a Manager by simply calling
the ``.register(...)`` method of a Component or by using the short-hand
``+`` or ``+=`` syntax. For example:

.. code-block:: python
   :linenos:


   from circuits import handler, Event, Component, Debugger

   class Add(Event):
      """Add Event"""

   class Print(Event):
      """Print Event"""

      end = "print_ended",

   class Adder(Component):

      @handler("add")
      def onAdd(self, x, y):
         self.push(Print(x + y))

   class Printer(Component):

      @handler("print")
      def onPrint(self, s):
         print s

   class System(Component):

      def __init__(self):
         super(System, self).__init__()

         Debugger().register(self)
         self += (Adder() + Printer())

      def started(self, component, mode):
         self.push(Add(4, 5))

      def print_ended(self, e, h, v):
         raise SystemExit, 0

   System().run()


Although this example above seems quite complex and uses quite a few of
circuits' features, it is actually quite simple. You can learn more
about some of the features used above in later documentation but the key
things here are lines 28 and 29 showing the different ways of registering
components.

Here's the output of the above example system/application:

.. code-block:: sh

   $ python demo.py
   <Registered[*:registered] [<Debugger/* (queued=0, channels=1, handlers=1) [S]>, <System/* (queued=0, channels=5, handlers=5) [R]>] {}>
   <Registered[*:registered] [<Printer/* (queued=0, channels=1, handlers=1) [S]>, <Adder/* (queued=0, channels=2, handlers=2) [S]>] {}>
   <Registered[*:registered] [<Adder/* (queued=0, channels=2, handlers=2) [S]>, <System/* (queued=0, channels=5, handlers=5) [R]>] {}>
   <Started[*:started] [<System/* (queued=0, channels=5, handlers=5) [R]>, None] {}>
   <Add[*:add] [4, 5] {}>
   <Print[*:print] [9] {}>
   9
   <End[*:print_ended] [<Print[*:print] [9] {}>, <bound method Printer.onPrint of <Printer/* (queued=0, channels=1, handlers=1) [S]>>, None] {}>

Don't worry about understanding the output above right now. Most of this is
events flowing through the system and printed to the screen by the Debugger
Component so you can see what's going on.

Running/Starting Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As stated, you can start a Component in one of three ways. Line #37 in the
above example could have been one of:

.. code-block:: python

   System().run() # start in main thread.


.. code-block:: python

   System().start() # start in a new separate thread.


.. code-block:: python

   System().start(process=True) # start in a new separate process.


Values and Future Values
------------------------

Now no Event-Driven, Asynchronous Framewotk with a Component Architecture would
be complete unless you could do useful things like compute values, nested
values (*those which have not been computed yet*) and future values
(*values which take time to compute - potentially blocking*).

circuits has built-in support for all of this and more!

Let's look at two commonly used features, Values and Future Values...

Values
~~~~~~

Everytime you push/fire an Event, the return value is a ``Value`` object
with some very useful properties and behaviors.

Let's consider the following python interactive session:

.. code-block:: python

   >>> from circuits import Event, Component
   >>> class Test(Component):
   ...    def event(self, x, y):
   ...       return x + y
   ...
   >>> test = Test()
   >>> test.start()
   >>> x = test.push(Event(4, 5))
   >>> print x
   9

``x`` in the session above is an instance of a ``Value`` which is used to
hold and represent the final computed value of an Event and its associated
Event Handlers.

Future Values
~~~~~~~~~~~~~

Future Values are very similar to Values, the only difference being that
a Future Value is computed in a Thread and the Event Handler executed in
this new Thread. This is to ensure that potentially blocking operations
do not block and are asynchronous.

A quick modification of the previous example to demonstrate:

.. code-block:: python

      >>> from time import sleep
   >>> from circuits import future, Event, Component
   >>> class Test(Component):
   ...    @future()
   ...    def event(self, x, y):
   ...       sleep(5) # simulate long computation
   ...       return x + y
   ...
   >>> test = Test()
   >>> test.start()
   >>> x = test.push(Event(4, 5))
   >>> x.result
   False
   >>> print x
   9
   >>> x.result
   True

The first time ``x.result`` is evaluated, it is ``False`` as the Event Handler
has not yet completed and the computation has not finished. The 2nd time
we try to use ``x`` (*after 5s*), we get its computed value. The entire
operations is non-blocking/asynchronous.

Networking and I/O
------------------

As you'd expect, circuits does come complete with non-blocking/asynchronous
networking and i/o components allowing you to build systems and applications
that require network/socket and file operations. This tutorial however is
not intended as an introduction to Networking, Socket Programming, etc...

Instead here are three very simple examples to serve as demonstrations
of Server/Client sockets and File I/O:

Echo Server:

.. code-block:: python
   :linenos:

   from circuits.net.sockets import TCPServer, Write

   class EchoServer(TCPServer):

      def read(self, sock, data):
         self.push(Write(sock, data))

   EchoServer(8000).run()

Echo Client:

.. code-block:: python
   :linenos:

   from circuits.io import stdin
   from circuits import handler, Component
   from circuits.net.sockets import TCPClient, Connect, Write

   class EchoClient(Component):

      channel = "echo"

      stdin = stdin

      def __init__(self):
         super(EchoClient, self).__init__()

         TCPClient(channel=self.channel).register(self)
         self.push(Connect("127.0.0.1", 8000))

      def connected(self, host, port):
         print "Connected to %s:%d" % (host, port)

      def read(self, data):
         print data.strip()

      @handler("read", target=stdin)
      def stdin_read(self, data):
         self.push(Write(data))

   EchoClient().run()

Cat:

.. code-block:: python
   :linenos:

   import sys

   from circuits.io import stdout, File, Write

   class Cat(File):

      stdout = stdout

      def read(self, data):
         self.push(Write(data), target=stdout)

      def eof(self):
         raise SystemExit, 0

   Cat(sys.argv[1]).run()


circuits comes shipped with the following networking, polling and i/o support:

* Sockets: TCPServer, TCPClient, UDPServer, UDPClient, UNIXServer, UNIXClient
            and Pipe
* Pollers: Select, Poll and EPoll
* I/O: File and Serial

Development Tools
-----------------

circuits includes various tools useful while developing a system/application.

Debugger
~~~~~~~~

Often while developing a new system/application, you'd like to know what's
going on and the sequence of events flowing through the system.

circuits contains a builtin ``Debugger`` Component for this very purpose
with file and logging support. To use it simply register it to the system.

Example:

.. code-block:: python
   :linenos:

   from circuits import Component, Debugger

   class System(Component):
      """My System"""

   (System() + Debugger()).run()


Tools
~~~~~

``circuits.tools`` contains various utility functions also useful for
development, debugging, etc. The two most common that you'll likely
use are:

* ``inspect(x)``: print a detailed report of the system/component.
* ``graph(x)``: print (*and optionally create a .dot/.png*) graph of the system structure.
