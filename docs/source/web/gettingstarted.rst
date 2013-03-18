.. _web_getting_started:

Getting Started
===============

Just like any application or system built with circuits, a circuits.web
application follows the standard Component based design and structure
whereby functionality is encapsulated in components. circuits.web
itself is designed and built in this fashion. For example a circuits.web
Server's structure looks like this:

.. image:: ../images/CircuitsWebServer.png

To illustrate the basic steps, we will demonstrate developing
your classical "Hello World!" applications in a web-based way
with circuits.web

To get started, we first import the necessary components:

.. code-block:: python
   
   from circutis.web import Server, Controller
   

Next we define our first Controller with a single Request Handler
defined as our index. We simply return "Hello World!" as the response
for our Request Handler.

.. code-block:: python
   
   class Root(Controller):
   
      def index(self):
         return "Hello World!"
   

This completes our simple web application which will respond with
"Hello World!" when anyone accesses it.

*Admittedly this is a stupidly simple web application! But circuits.web is
very powerful and plays nice with other tools.*

Now we need to run the application:

.. code-block:: python
   
   (Server(8000) + Root()).run()
   

That's it! Navigate to: http://127.0.0.1:8000/ and see the result.

Here's the complete code:

.. code-block:: python
   :linenos:

   from circuits.web import Server, Controller
   
   class Root(Controller):
   
      def index(self):
         return "Hello World!"
   
   (Server(8000) + Root()).run()
   

Have fun!
