Miscellaneous
=============


Writing Tools
-------------

Most of the internal tools used by circuits.web in circuits.web.tools are
simply functions that modify the Request or Response objects in some way or
another... We won't be covering that here... What we will cover is how to
build simple tools that do something to the Request or Response along it's
life-cycle.

Here is a simple example of a tool that uses the pytidylib library to tidy
up the HTML output before it gets sent back to the requesting client.

Code:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    from tidylib import tidy_document

    from circuits import Component

    class Tidy(Component):

        channel = "http"

        def response(self, response):
            document, errors = tidy_document("".join(response.body))
            response.body = document
    Usage:

    (Server(8000) + Tidy() + Root()).run()
    
**How it works:**

This tool works by intercepting the Response Event on the "response" channel
of the "http" target (*or Component*). For more information about the
life cycle of Request and Response events, their channels and where and
how they can be intercepted to perform various tasks read the Request/Response
Life Cycle section.


Writing Dispatchers
-------------------


In circuits.web writing a custom "dispatcher" is only a matter of writing a
Component that listens for incoming Request events on the "request" channel
of the "web" target. The simplest kind of "dispatcher" is one that simply
modifies the request.path in some way. To demonstrate this we'll illustrate
and describe how the !VirtualHosts "dispatcher" works.

VirtualHosts code:

.. code-block:: python
    :linenos:

    class VirtualHosts(Component):

        channel = "web"

        def __init__(self, domains):
            super(VirtualHosts, self).__init__()

            self.domains = domains

        @handler("request", filter=True, priority=1)
        def request(self, event, request, response):
            path = request.path.strip("/")

            header = request.headers.get
            domain = header("X-Forwarded-Host", header("Host", ""))
            prefix = self.domains.get(domain, "")

            if prefix:
                path = _urljoin("/%s/" % prefix, path)
                request.path = path
    
The important thing here to note is the Event Handler listening on the
appropriate channel and the request.path being modified appropriately.

You'll also note that in [source:circuits/web/dispatchers.py] all of the
dispatchers have a set priority. These priorities are defined as::
    
    $ grin "priority" circuits/web/dispatchers/
    circuits/web/dispatchers/dispatcher.py:
       92 :     @handler("request", filter=True, priority=0.1)
    circuits/web/dispatchers/jsonrpc.py:
       38 :     @handler("request", filter=True, priority=0.2)
    circuits/web/dispatchers/static.py:
       59 :     @handler("request", filter=True, priority=0.9)
    circuits/web/dispatchers/virtualhosts.py:
       49 :     @handler("request", filter=True, priority=1.0)
    circuits/web/dispatchers/websockets.py:
       53 :     @handler("request", filter=True, priority=0.2)
    circuits/web/dispatchers/xmlrpc.py:
       36 :     @handler("request", filter=True, priority=0.2)
    
in web applications that use multiple dispatchers these priorities set
precedences for each "dispatcher" over another in terms of who's handling
the Request Event before the other.

.. note:: Some dispatchers are designed to filter the Request Event and prevent it from being processed by other dispatchers in the system.
