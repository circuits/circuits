How to build a Simple Server
============================


Overview
--------

In this guide we're going to walk through the steps required to build a
simple chat server. Users will connect using a standard telnet client and
start chatting with other users that are connected.


Prerequisites
.............

- `Python <http://www.python.org>`_
- `circuits <http://pypi.python.org/circuits>`_


Components
..........

- :py:class:`~circuits.core.components.Component`
- :py:class:`~circuits.net.sockets.TCPServer`


Step 1 - Setting up
-------------------

Let's start off by importing the components we need:

.. code-block:: python

   #!/usr/bin/env python

   from circuits import Component
   from circuits.net.sockets import TCPServer, Write


Step 2 - Building the Server
----------------------------

Next let's define our ``Server`` Component with a simple event handler that
broadcats all incoming messages to every connected client.

.. code-block:: python
   
   class Server(Component):
   
       def __init__(self, host, port=8000):
           super(Server, self).__init__()
   
           self._clients = []
   
           TCPServer((host, port)).register(self)
   
       def connect(self, sock, host, port):
           self._clients.append(sock)
   
       def disconnect(self, sock):
           self._clients.remove(sock)
   
       def read(self, sock, data):
           for client in self._clients:
               if not client == sock:
                   self.fire(Write(client, data.strip()))
   
Server("localhost").run()
Let's walk through this in details:

1. Create a new Component called ``Server``
2. Define its initialization arguments as ``(host, port=8000)``
3. Call the super constructor of the underlying Component
   (*This is important as all components need to be initialized properly*)
4. Register a ``TCPServer`` Component and configure it.
5. Create Event Handlers for:

   - Dealgin with new connecting clients.
   - Dealing with clients whom have disconnected
   - Dealing with messages from connected clients


Step 3 - Running the Server
---------------------------

The last step is simply to create an instance of the ``Server`` Component
and run it (*making sure to configure it with a host and port*).

.. code-block:: python
   
   Server("localhost").run()

That's it!

Using a standard telnet client try connecting to localhost on port 8000.
Try connecting a second client and watch what happens in the 2nd client
when you type text into the 1st.

Enjoy!


Source Code
-----------

.. literalinclude:: server.py
   :language: python
   :linenos:

:download:`Download server.py <server.py>`
