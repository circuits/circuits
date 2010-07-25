Introduction
============

circuits.web is a set of components for building high performance HTTP/1.1
and WSGI/1.0 compliant web applications. These components make it easy to
rapidly develop rich, scalable web applications with minimal effort.

circuits.web borrows from

* `CherryPy <http://www.cherrypy.org>`_
* BaseHTTPServer (*Python std. lib*)
* wsgiref (*Python std. lib*)

Overview
--------

The ``circuits.web`` namespace contains the following exported components
and events for convenience:

Events
~~~~~~

+---------------+-----------------------------------+
| Event         | Description                       |
+===============+===================================+
| Request       | The Request Event                 |
+---------------+-----------------------------------+
| Response      | The Response Event                |
+---------------+-----------------------------------+
| Stream        | The Stream Event                  |
+---------------+-----------------------------------+

Servers
~~~~~~~

+---------------+-----------------------------------+
| Server        | Description                       |
+===============+===================================+
| BaseServer    | The Base Server (no Dispatcher)   |
+---------------+-----------------------------------+
| Server        | The **full** Server + Dispatcher  |
+---------------+-----------------------------------+

Error Events
~~~~~~~~~~~~

+---------------+-----------------------------------+
| Error         | Description                       |
+===============+===================================+
| HTTPError     | A generic HTTP Error Event        |
+---------------+-----------------------------------+
| Forbidden     | A Forbidden (403) Event           |
+---------------+-----------------------------------+
| NotFound      | A Not Found (404) Event           |
+---------------+-----------------------------------+
| Redirect      | A Redirect (30x) Event            |
+---------------+-----------------------------------+

Dispatchers
~~~~~~~~~~~

+---------------+-----------------------------------+
| Dispatcher    | Description                       |
+===============+===================================+
| Static        | A Static File Dispatcher          |
+---------------+-----------------------------------+
| Dispatcher    | The Default Dispatcher            |
+---------------+-----------------------------------+
| VirtualHosts  | Virtual Hosts Dispatcher          |
+---------------+-----------------------------------+
| XMLRPC        | XML-RPC Dispatcher                |
+---------------+-----------------------------------+
| JSONRPC       | JSON-RPC Dispatcher               |
+---------------+-----------------------------------+

Other Components
~~~~~~~~~~~~~~~~

+---------------+-----------------------------------+
| Component     | Description                       |
+===============+===================================+
| Logger        | Default Logger                    |
+---------------+-----------------------------------+
| Controller    | Request Handler Mapper            |
+---------------+-----------------------------------+
| Sessions      | Default Sessions Handler          |
+---------------+-----------------------------------+

To start working with circuits.web one normally only needs to import
from circuits.web, for example:

.. code-block:: python
   :linenos:

   from circuits import Component
   from circuits.web import BaseServer

   class Root(Component):

       def request(self, request, response):
           return "Hello World!"

   (BaseServer(8000) + Root()).run()

For further information regarding any of circuits.web's components,
events or other modules and functions refer to the API Documentation.
