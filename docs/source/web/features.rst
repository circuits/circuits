.. _CherryPy: http://www.cherrypy.org/


.. module:: circuits.web


Features
========


circuits.web is not a **Full Stack** or **High Level** web framework, rather
it is more closely aligned with `CherryPy`_ and offers enough functionality
to make quickly developing web applications easy and as flexible as possible.

circuits.web does not provide high level features such as:

- Templating
- Database access
- Form Validation
- Model View Controller
- Object Relational Mapper

The functionality that circutis.web **does** provide ensures that
circuits.web is fully HTTP/1.1 and WSGI/1.0 compliant and offers all the
essential tools you need to build your web application or website.

To demonstrate each feature, we're going to use the classical "Hello World!"
example as demonstrated earlier in :doc:`gettingstarted`.

Here's the code again for easy reference:

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller
    
    
    class Root(Controller):
        
        def index(self):
            return "Hello World!"
    
    
    (Server(8000) + Root()).run()


Logging
-------


circuits.web's :class:`~.Logger` component  allows
you to add logging support compatible with Apache
log file formats to your web application.

To use the :class:`~Logger` simply add it to your application:

.. code-block:: python
    
    (Server(8000) + Logger() + Root()).run()

Example Log Output::
    
    127.0.0.1 - - [05/Apr/2014:10:13:01] "GET / HTTP/1.1" 200 12 "" "curl/7.35.0"
    127.0.0.1 - - [05/Apr/2014:10:13:02] "GET /docs/build/html/index.html HTTP/1.1" 200 22402 "" "curl/7.35.0"


Cookies
-------


Access to cookies are provided through the :class:`~.Request` Object which holds data
about the request. The attribute :attr:`~.Request.cookie` is provided as part of the
:class:`~.Request` Object. It is a dict-like object, an instance of ``Cookie.SimpleCookie``
from the python standard library.

To demonstrate "Using Cookies" we'll write a very simple application that
remembers who we are:

If a cookie **name** is found, display "Hello <name>!".
Otherwise, display "Hello World!"
If an argument is given or a query parameter **name** is given,
store this as the **name** for the cookie.
Here's how we do it:

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller
    
    
    class Root(Controller):
        
        def index(self, name=None):
            if name:
                self.cookie["name"] = name
            else:
                name = self.cookie.get("name", None)
                name = "World!" if name is None else name.value
            
            return "Hello {0:s}!".format(name)
    
    
    (Server(8000) + Root()).run()

.. note:: To access the actual value of a cookie use the ``.value`` attribute.

.. warning:: Cookies can be vulnerable to XSS (*Cross Site Scripting*) attacks
             so use them at your own risk. See: http://en.wikipedia.org/wiki/Cross-site_scripting#Cookie_security


Dispatchers
-----------

circuits.web provides several dispatchers in the :mod:`~.dispatchers` module.
Most of these are available directly from the circuits.web namespace by
simply importing the required "dispatcher" from circuits.web.

Example:

.. code-block:: python
    
    from circuits.web import Static

The most important "dispatcher" is the default :class:`~.Dispatcher` used by the
circuits.web :class:`~.Server` to dispatch incoming requests onto a channel mapping
(*remember that circuits is event-driven and uses channels*), quite similar to that of CherryPy
or any other web framework that supports object traversal.

Normally you don't have to worry about any of the details of the *default*
:class:`~.Dispatcher` nor do you have to import it or use it in any way as it's already
included as part of the circuits.web :class:`~.Server` Component structure.


Static
......


The :class:`~.Static` "dispatcher" is used for serving static resources/files
in your application. To use this, simply add it to your application. It takes
some optional configuration which affects it's behavior.

The simplest example (*as per our Base Example*):

.. code-block:: python
    
    (Server(8000) + Static() + Root()).run()

This will serve up files in the *current directory* as static resources.

.. note::  This may override your **index** request handler of your top-most
           (``Root``) :class:`~.Controller`. As this might be undesirable and
           it's normally  common to serve static resources via a different path
           and even have them stored in a separate physical file path, you can
           configure the Static "dispatcher".

Static files stored in ``/home/joe/www/``:

.. code-block:: python
    
    (Server(8000) + Static(docroot="/home/joe/www/") + Root()).run()

Static files stored in ``/home/joe/www/`` **and** we want them served up as
``/static`` URI(s):

.. code-block:: python
    
    (Server(8000) + Static("/static", docroot="/home/joe/www/") + Root()).run()


Dispatcher
..........


The :class:`~.Dispatcher` (*the default*) is used to dispatch requests
and map them onto channels with a similar URL Mapping as CherryPy's.
A set of "paths" are maintained by the Dispatcher as Controller(s) are
registered to the system or unregistered from it. A channel mapping is
found by traversing the set of known paths (*Controller(s)*) and
successively matching parts of the path (*split by /*) until a suitable
Controller and Request Handler is found. If no Request Handler is found
that matches but there is a "default" Request Handler, it is used.

This Dispatcher also included support for matching against HTTP methods:

- GET
- POST
- PUT
- DELETE.
  
Here are some examples:

.. code-block:: python
    :linenos:
    
    class Root(Controller):
    
        def index(self):
            return "Hello World!"
        
        def foo(self, arg1, arg2, arg3):
            return "Foo: %r, %r, %r" % (arg1, arg2, arg3)
        
        def bar(self, kwarg1="foo", kwarg2="bar"):
            return "Bar: kwarg1=%r, kwarg2=%r" % (kwarg1, kwarg2)
        
        def foobar(self, arg1, kwarg1="foo"):
            return "FooBar: %r, kwarg1=%r" % (arg1, kwarg1)

With the following requests::
    
    http://127.0.0.1:8000/
    http://127.0.0.1:8000/foo/1/2/3
    http://127.0.0.1:8000/bar?kwarg1=1
    http://127.0.0.1:8000/bar?kwarg1=1&kwarg=2
    http://127.0.0.1:8000/foobar/1
    http://127.0.0.1:8000/foobar/1?kwarg1=1

The following output is produced::
    
    Hello World!
    Foo: '1', '2', '3'
    Bar: kwargs1='1', kwargs2='bar'
    Bar: kwargs1='1', kwargs2='bar'
    FooBar: '1', kwargs1='foo'
    FooBar: '1', kwargs1='1'

This demonstrates how the Dispatcher handles basic paths and how it handles
extra parts of a path as well as the query string. These are essentially
translated into arguments and keyword arguments.

To define a Request Handler that is specifically for the HTTP ``POST`` method, simply define a Request Handler like:

.. code-block:: python
    :linenos:
    
    class Root(Controller):
        
        def index(self):
            return "Hello World!"
       
    
    class Test(Controller):
        
        channel = "/test"
        
        def POST(self, *args, **kwargs): #***
            return "%r %r" % (args, kwargs)

This will handles ``POST`` requests to "/test", which brings us to the final
point of creating URL structures in your application. As seen above to create
a sub-structure of Request Handlers (*a tree*) simply create another
:class:`~.Controller` Component giving it a different channel and add it to the system
along with your existing Controller(s).


.. warning:: All public methods defined in your :class:`~.Controller`(s) are exposed
             as valid URI(s) in your web application. If you don't want
             something exposed either subclass from :class:`~BaseController` whereby
             you have to explicitly use :meth:`~.expose` or use ``@expose(False)``
             to decorate a public method as **NOT Exposed** or simply prefix the desired
             method with an underscore (e.g: ``def _foo(...):``).


VirtualHosts
............


The :class:`~.VirtualHosts` "dispatcher" allows you to serves up different parts of
your application for different "virtual" hosts.

Consider for example you have the following hosts defined::
    
    localdomain
    foo.localdomain
    bar.localdomain

You want to display something different on the default domain name
"localdomain" and something different for each of the sub-domains
"foo.localdomain" and "bar.localdomain".

To do this, we use the VirtualHosts "dispatcher":

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller, VirtualHosts
    
    
    class Root(Controller):
        
        def index(self):
            return "I am the main vhost"
    
    
    class Foo(Controller):
        
        channel = "/foo"
        
        def index(self):
            return "I am foo."
    
    
    class Bar(Controller):
        
        channel = "/bar"
        
        def index(self):
            return "I am bar."
    
    
    domains = {
        "foo.localdomain:8000": "foo",
        "bar.localdomain:8000": "bar",
    }
    
    
    (Server(8000) + VirtualHosts(domains) + Root() + Foo() + Bar()).run()

With the following requests::
    
    http://localdomain:8000/
    http://foo.localdomain:8000/
    http://bar.localdomain:8000/

The following output is produced::
    
    I am the main vhost
    I am foo.
    I am bar.

The argument **domains** pasted to VirtualHosts' constructor is a mapping
(*dict*) of: domain -> channel


XMLRPC
......


The :class:`~.XMLRPC` "dispatcher" provides a circuits.web application with the capability of serving up RPC Requests encoded in XML (XML-RPC).

Without going into too much details (*if you're using any kind of RPC "dispatcher" you should know what you're doing...*), here is a simple example:

.. code-block:: python
    :linenos:
    
    from circuits import Component
    from circuits.web import Server, Logger, XMLRPC
    
    
    class Test(Component):
        
        def foo(self, a, b, c):
            return a, b, c
    
    
    (Server(8000) + Logger() + XMLRPC() + Test()).run()

Here is a simple interactive session::
    
    >>> import xmlrpclib
    >>> xmlrpc = xmlrpclib.ServerProxy("http://127.0.0.1:8000/rpc/")
    >>> xmlrpc.foo(1, 2, 3)
    [1, 2, 3]
    >>> 


JSONRPC
.......

The :class:`~.JSONRPC` "dispatcher" is Identical in functionality to the :class:`~.XMLRPC` "dispatcher".

Example:

.. code-block:: python
    :linenos:
    
    from circuits import Component
    from circuits.web import Server, Logger, JSONRPC
    
    
    class Test(Component):
        
        def foo(self, a, b, c):
            return a, b, c
    
    
    (Server(8000) + Logger() + JSONRPC() + Test()).run()

Interactive session (*requires the `jsonrpclib <https://pypi.python.org/pypi/jsonrpc>`_ library*)::
    
    >>> import jsonrpclib
    >>> jsonrpc = jsonrpclib.ServerProxy("http://127.0.0.1:8000/rpc/")
    >>> jsonrpc.foo(1, 2, 3)
    {'result': [1, 2, 3], 'version': '1.1', 'id': 2, 'error': None}
    >>> 


Caching
-------

circuits.web includes all the usual **Cache Control**, **Expires**
and **ETag** caching mechanisms.

For simple expires style caching use the :meth:`~.tools.expires` tool from :mod:`.circuits.web.tools`.

Example:

.. code-block:: python
   :linenos:
    
    from circuits.web import Server, Controller
    
    
    class Root(Controller):
        
        def index(self):
            self.expires(3600)
            return "Hello World!"
    
    
    (Server(8000) + Root()).run()

For other caching mechanisms and validation please
refer to the :mod:`circuits.web.tools` documentation.

See in particular:

- :meth:`~.tools.expires`
- :meth:`~.tools.validate_since`

.. note:: In the example above we used ``self.expires(3600)`` which is
          just a convenience method built into the :class:`~.Controller`.
          The :class:`~.Controller` has other such convenience methods
          such as ``.uri``, ``.forbidden()``, ``.redirect()``, ``.notfound()``,
          ``.serve_file()``, ``.serve_download()`` and ``.expires()``.

          These are just wrappers around :mod:`~.tools` and :mod:`~.events`.


Compression
-----------

circuits.web includes the necessary low-level tools in order to achieve
compression. These tools are provided as a set of functions that can be
applied to the response before it is sent to the client.

Here's how you can create a simple Component that enables compression
in your web application or website.

.. code-block:: python
    :linenos:
    
    from circuits import handler, Component
    
    from circuits.web.tools import gzip
    from circuits.web import Server, Controller, Logger
    
    
    class Gzip(Component):
        
        @handler("response", priority=1.0)
        def compress_response(self, event, response):
            event[0] = gzip(response)
    
    
    class Root(Controller):
        
        def index(self):
            return "Hello World!"
    
    
    (Server(8000) + Gzip() + Root()).run()


Please refer to the documentation for further details:

- :func:`.tools.gzip`
- :func:`.utils.compress`


Authentication
--------------

circuits.web provides both HTTP Plain and Digest Authentication provided by the functions in :mod:`circuits.web.tools`:

- :func:`.tools.basic_auth`
- :func:`.tools.check_auth`
- :func:`.tools.digest_auth`

The first 2 arguments are always (*as with most circuits.web tools*):

- ``(request, response)``

An example demonstrating the use of "Basic Auth":

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller
    from circuits.web.tools import check_auth, basic_auth
    
    
    class Root(Controller):
        
        def index(self):
            realm = "Test"
            users = {"admin": "admin"}
            encrypt = str
            
            if check_auth(self.request, self.response, realm, users, encrypt):
                return "Hello %s" % self.request.login
            
            return basic_auth(self.request, self.response, realm, users, encrypt)
    
    
    (Server(8000) + Root()).run()

For "Digest Auth":

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller
    from circuits.web.tools import check_auth, digest_auth
    
    
    class Root(Controller):
        
        def index(self):
            realm = "Test"
            users = {"admin": "admin"}
            encrypt = str
            
            if check_auth(self.request, self.response, realm, users, encrypt):
                return "Hello %s" % self.request.login
            
            return digest_auth(self.request, self.response, realm, users, encrypt)
    
    
    (Server(8000) + Root()).run()


Session Handling
----------------

Session Handling in circuits.web is very similar to Cookies.
A dict-like object called **.session** is attached to every
Request Object during the life-cycle of that request. Internally
a Cookie named **circuits.session** is set in the response.

Rewriting the Cookie Example to use a session instead:

.. code-block:: python
    :linenos:
    
    from circuits.web import Server, Controller, Sessions
    
    
    class Root(Controller):
        
        def index(self, name=None):
            if name:
                self.session["name"] = name
            else:
                name = self.session.get("name", "World!")
            
            return "Hello %s!" % name
    
    
    (Server(8000) + Sessions() + Root()).run()

.. note:: The only Session Handling provided is a
          temporary in-memory based one and will
          not persist. No future Session Handling
          components are planned. For persistent
          data you should use some kind of Database.
