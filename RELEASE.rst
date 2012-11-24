Release Notes - circuits-2.0.0 (cheetah)
----------------------------------------


Component Initialization
........................

Implemented ``Component.init()`` support whereby one can define an
alternative ``init()`` without needing to remember to call ``super(...)``
``init()`` takes the same arguments as the normal ``__init__(...)`` constructor.

Example:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   from circuits import Component

   class App(Component):

      def init(self, ...):
         ...


Component Singleton Support
...........................

No. This isn't anything crazy bout restricting what you can do with components.
This new feature allows you as a developer to restrict how many instances of
any given component can be running in any given system.

Say you defined a ``Logger`` Component but you only wanted and designed
for only one instance ever running in a single system. This is how you do it:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   from circuits import Component


   class App(Component):

      singleton = True


More Convenience for I/O Components
...................................


All I/O Components now implement the ``value_changed`` Event Notification API
allowing you to define ``read`` Event Handlers that simply return responses.

Example:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   """A Simple Echo Server"""


   from circuits.net.sockets import TCPServer


   class EchoServer(TCPServer):

      def read(self, sock, data):
         return data


   EchoServer(8000).run()


Tick Functions are now decorators!
..................................


In previous releases of circuits, a ``Component`` could only have a single
``__tick__`` (*Tick Function*). This restriction is now gone and we've made it
much simpler to define new *Tick Functions* by simply using the new ``@tick``
decorator.

Example:

.. code-block:: python
   :linenos:

   from circuits import tick

   class MyComponent(Component):
      @tick
      def my_tick(self):
         print 'time is passing'


callEvent/waitEvent Enhancements
.................................

In circuits-1.6 we introduced two new primitives.

 - ``.callEvent(...)``
 - ``.waitEvent(...)``

These two primitives introduced synchronous features to the circuits framework
allowing you to pause the execution of an event handler and write almost
synchronous-style code whilst remaining asynchronous in the background.

Here are the list of improvements and an example to go with.

- The ``.call(...)`` and ``.wait(...)`` synchronous primitives in this release
  are now implemented as co-routines using standard Python generators.
  (*Previously they were implemented using greenlets*).
- The API are identical to that of ``fire(...)``
- Added the ability to return values from ``callEvent``
- Added the ability to yield from an event handler.

.. code-block:: python
   :linenos:
      
   class A(Component):
   
       channel = "a"

       def foo(self):
           return "Hello"
   
   
   class B(Component):
   
       channel = "b"
   
       def foo(self):
           return "World!"
   
   
   class App(Component):
   
       def hello(self):
           a = yield self.call(Event.create("foo"), "a")
           b = yield self.call(Event.create("foo"), "b")
           yield "{0} {1}".format(a, b)
   
   m = Manager() + Debugger()
   A().register(m)
   B().register(m)
   App().register(m)
   m.start()


For a full list of changes for this release see the `Change Log <http://packages.python.org/circuits/changes.html>`_.
