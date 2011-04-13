.. _Python Programming Language: http://www.python.org/


Tutorial
========


Overview
--------

Welcome to the circuits tutorial. This 5-minute tutorial is going to walk you
through the basic concepts of circuits. The goal will be to introduce
new concepts incrementally with walk-through examples that you can try out!
By the time you've finished, you should have a good basic understanding
of circuits, how it feels and where to go from there.


The Component
-------------

First up, let's show how you can use the ``Component`` and run it in a very
simple application.

.. literalinclude:: 001.py
   :language: python
   :linenos:

:download:`Download 001.py <001.py>`

Okay so that's pretty boring as it doesn't do very much! But that's okay...
Read on!

Let's try to create our own custom Component called ``MyComponent``.

.. literalinclude:: 002.py
   :language: python
   :linenos:

:download:`Download 002.py <002.py>`

Okay, so this still isn't very sueful! But at least we can create
components with the behavior we want.

Let's move on to something more interesting...


Event Handlers
--------------

Let's now extend our little example to say "Hello World!" when it's
started.

.. literalinclude:: 003.py
   :language: python
   :linenos:

:download:`Download 003.py <003.py>`

Here we've created a simple **Event Handler** that listens for events on
the "started" channel. Methods defined in a Component are converted into
Event Handlers.

Running this we get::
   
   Hello World!


Alright! We have something slightly more useful! Whoohoo it says hello!

.. note:: Press ^C (*Ctrl + C*) to exit.


Registering Components
----------------------

So now that we've learned how to use a Component, create a custom Component
and create simple Event Handlers, let's try something a bit more complex
and create two components that each do something fairly simple.

Let's create two components:

- ``Bob``
- ``Fred``

.. literalinclude:: 004.py
   :language: python
   :linenos:

:download:`Download 004.py <004.py>`

Notice the way we register the two components ``Bob`` and ``Fred`` together
? Don't worry if this doesn't make sense right now. Think of it as putting
two components together and plugging them into a circuits board.

Running this example produces the following result::
   
   Hello I'm Bob!
   Hello I'm Fred!

Cool! We have two components that each do something and print a simple
message on the screen!


Complex Components
------------------

Now, what if we wanted to create a Complex Component ? Let's say we wanted
to create a new Component made up of two other smaller components ?

We can do this by simply registering components to a Complex Component
during initialization.

.. literalinclude:: 005.py
   :language: python
   :linenos:

:download:`Download 005.py <005.py>`

So now ``Pound`` is a Component that consists of two other components
registered to it: ``Bob`` and ``Fred``

The output of this is identical to the previous::
   
   Hello I'm Bob!
   Hello I'm Fred!

The only difference is that ``Bob`` and ``Fred`` are now part of a more
Complex Component called ``Pound``. This can be illustrated by the
following diagram:

.. graphviz::
   
   digraph G {
      "Pound-1344" -> "Bob-9b0c";
      "Pound-1344" -> "Fred-e98a";
   }
   
Cool :-)


Component Inheritence
---------------------

Since circuits is a framework written for the `Python Programming
Language`_ it naturally inherits properties of Object Orientated
Programming (OOP) -- such as inheritence.

So let's take our ``Bob`` and ``Fred`` components and create a Base
Component called ``Dog`` and modify our two dogs (``Bob`` and ``Fred``) to
subclass this.

.. literalinclude:: 006.py
   :language: python
   :linenos:

:download:`Download 006.py <006.py>`

Now let's try to run this and see what happens::
   
  Woof! I'm Bob!
  Woof! I'm Fred!

So both dogs barked~ Hmmm


Component Channels
------------------

What if we only want one of our dogs to bark ? How do we do this without
causing the other one to bark as well ?

Easy! Use a separate ``channel`` like so:

.. literalinclude:: 007.py
   :language: python
   :linenos:

:download:`Download 007.py <007.py>`

If you run this, you'll get::
   
   Woof! I'm Bob!


Hopefully this gives you a feel of what circuits is all about and a easy
tutorial on some of the basic concepts. As you're no doubt itching to get
started on your next circuits project, here's some recommended reading:

- :doc:`../faq`
- :doc:`../guides/index`
- :doc:`../api/index`
