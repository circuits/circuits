The Basics
==========

circuits.web is not a **full stack** web framework, rather
it is more closely aligned with `CherryPy <http://www.cherrypy.org>`_
and offers enough functionality to make quickly developing web applications
easy and as flexible as possible. circuits.web does not provide features such
as:

* builtin Templating
* builtin Database or ORM tools
* **etc**

The functionality that circutis.web *does* provide ensures that circuits.web
is fully HTTP/1.1 and WSGI/1.0 compliant and offers all the essential tools
you need to build your web application or website.

A Stand Alone Server
--------------------

A stand alone server consist of the components shown in section
:ref:`web_getting_started`. The process of handling an HTTP request starts
with the :class:`~circuits.net.sockets.TCPServer` receiving a chunk
of bytes. It emits those bytes as a :class:`~circuits.net.sockets.Read`
event on the channel shared by the Server, HTTP, TCPServer and
Dispatcher components ("web" by default). 

The Read events are handled by the 
:class:`~circuits.web.http.HTTP` component. It collects the chunks until
a complete HTTP request has been received. The request is then emitted as
a :class:`~circuits.web.events.Request` event with an instance of 
classes :class:`~circuits.web.wrappers.Request` and
:class:`~circuits.web.wrappers.Response` each as arguments. To complete
the client's request, a :class:`~circuits.web.events.Response` event must be
fired. This is usually done by the HTTP component itself upon the
receipt of a ``RequestSuccess`` event (automatically generated
after all handlers for the ``Request`` event have been invoked
successfully). In case of a problem, the ``Request`` event's handlers should
fire or return a :class:`~circuits.web.errors.HTTPError` which is instead 
converted by the HTTP component to a ``Response`` event.
 
HTTP's handler for the :class:`~circuits.web.events.Response`
event retrieves the response information from the 
event and encodes it as required by HTTP (the protocol). It then 
fires one or more :class:`~circuits.net.sockets.Write` events
which are handled by the TCPServer (and the response is thus sent to 
the client). More details can be found in :ref:`circuits_web_http`.

A commonly used component for handling :class:`~circuits.web.events.Request` 
events is a dispatcher. [To be continued]