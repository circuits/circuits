Release Notes - circuits-2.0.0 (cheetah)
----------------------------------------

- Implemented ``Component.init()`` support whereby one can define an
  alternative ``init()`` without needing to remember to call ``super(...)``
  ``init()`` takes the same arguments as the normal ``__init__(...)``
  constructor.
  Example:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   from circuits import Component

   class App(Component):

      def init(self, ...):
         ...

- Added Singleton support. It is now possible to specify that a component
  only be registered once. For example:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   from circuits import Component


   class App(Component):

      singleton = True

- Added support for ``value_changed`` event notifications on the ``read``
  channels for sockets. This enables you to specify much simpler event
  handlers that handle requests. For example:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python

   """A Simple Echo Server"""


   from circuits.net.sockets import TCPServer


   class EchoServer(TCPServer):

      def read(self, sock, data):
         return data


   EchoServer(8000).run()

- Changed how ticks are defined

.. code-block:: python
   :linenos:

   from circuits import tick

   class MyComponent(Component):
      @tick
      def my_tick(self):
         print 'time is passing'

- Added the ability to return values from callEvent

.. code-block:: python
   :linenos:

   class ProcessData(Event):
      pass

   class MyComponent(Component):
      def process_data(self, data):
          return data

      def on_read(self, data):
         processed_data = self.callEvent(ProcessData(data))
         print process_data


For a full list of changes for this release see the `Change Log <http://packages.python.org/circuits/changes.html>`_.
