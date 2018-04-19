.. module:: circuits


How To Guides
=============


These "How To" guides will steer you in the right direction for common
aspects of modern web applications and website design.


How Do I: Use a Templating Engine
---------------------------------


circuits.web tries to stay out of your way as much as possible and doesn't
impose any restrictions on what external libraries and tools you can use
throughout your web application or website. As such you can use any template
language/engine you wish.


Example: Using Mako
...................


This basic example of using the Mako Templating Language.
First a TemplateLookup instance is created. Finally a function called
``render(name, **d)`` is created that is used by Request Handlers to
render a given template and apply data to it.

Here is the basic example:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    import os
    

    import mako
    from mako.lookup import TemplateLookup
    
    
    from circuits.web import Server, Controller
    
    
    templates = TemplateLookup(
        directories=[os.path.join(os.path.dirname(__file__), "tpl")],
        module_directory="/tmp",
        output_encoding="utf-8"
    )
    
    
    def render(name, **d): #**
        try:
            return templates.get_template(name).render(**d) #**
        except:
            return mako.exceptions.html_error_template().render()
    
    
    class Root(Controller):
        
        def index(self):
            return render("index.html")
        
        def submit(self, firstName, lastName):
            msg = "Thank you %s %s" % (firstName, lastName)
            return render("index.html", message=msg)
    
    
    (Server(8000) + Root()).run()


Other Examples
..............

Other Templating engines will be quite similar to integrate.


How Do I: Integrate with a Database
-----------------------------------


.. warning:: Using databases in an asynchronous framework is problematic
             because most database implementations don't support asynchronous
             I/O operations.

             Generally the solution is to use threading to hand off
             database operations to a separate thread.

Here are some ways to help integrate databases into your application:

1. Ensure your queries are optimized and do not block
   for extensive periods of time.
2. Use a library like `SQLAlchemy <http://www.sqlalchemy.org/>`_
   that supports multi-threaded database operations
   to help prevent your circuits.web web application
   from blocking.
3. *Optionally* take advantage of the :class:`~circuits.Worker`
   component to fire :class:`~circuits.task` events wrapping
   database calls in a thread or process pool. You can then use
   the :meth:`~circuits.Component.call` and :meth:`~.circuits.Component.wait`
   synchronization primitives to help with the control flow of
   your requests and responses.

Another way you can help improve performance
is by load balancing across multiple backends
of your web application. Using things like
`haproxy <http://haproxy.1wt.eu/>`_ or
`nginx <http://nginx.org/en/>`_ for load balancing
can really help.


How Do I: Use WebSockets
------------------------


Since the :class:`~circuits.web.websockets.WebSocketDispatcher`
id a circuits.web "dispatcher" it's quite easy to
integrate into your web application. Here's a simple
trivial example:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    from circuits.net.events import write
    from circuits import Component, Debugger
    from circuits.web.dispatchers import WebSocketsDispatcher
    from circuits.web import Controller, Logger, Server, Static
    
    
    class Echo(Component):
        
        channel = "wsserver"
        
        def read(self, sock, data):
            self.fireEvent(write(sock, "Received: " + data))
    
    
    class Root(Controller):
        
        def index(self):
            return "Hello World!"
    
    
    app = Server(("0.0.0.0", 8000))
    Debugger().register(app)
    Static().register(app)
    Echo().register(app)
    Root().register(app)
    Logger().register(app)
    WebSocketsDispatcher("/websocket").register(app)
    app.run()

See the `circuits.web examples <https://github.com/circuits/circuits/tree/master/examples/web>`_.


How do I: Build a Simple Form
-----------------------------


circuits.web parses all POST data as a request comes through and creates a
dictionary of kwargs (Keyword Arguments) that are passed to Request Handlers.

Here is a simple example of handling form data:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    from circuits.web import Server, Controller
    
    
    class Root(Controller):
        
        html = """\
    <html>
     <head>
      <title>Basic Form Handling</title>
     </head>
     <body>
      <h1>Basic Form Handling</h1>
      <p>
       Example of using
       <a href="http://code.google.com/p/circuits/">circuits</a> and it's
       <b>Web Components</b> to build a simple web application that handles
       some basic form data.
      </p>
      <form action="submit" method="POST">
       <table border="0" rules="none">
        <tr>
         <td>First Name:</td>
         <td><input type="text" name="firstName"></td>
        </tr>
        <tr>
         <td>Last Name:</td>
         <td><input type="text" name="lastName"></td>
        </tr>
         <tr>
          <td colspan=2" align="center">
           <input type="submit" value="Submit">
         </td>
         </tr>
       </table>
      </form>
     </body>
    </html>"""
        
        
        def index(self):
            return self.html
        
        def submit(self, firstName, lastName):
            return "Hello %s %s" % (firstName, lastName)
    
    
    (Server(8000) + Root()).run(


How Do I: Upload a File
-----------------------


You can easily handle File Uploads as well using the same techniques as above.
Basically the "name" you give your <input> tag of type="file" will get passed
as the Keyword Argument to your Request Handler. It has the following two
attributes::
    
    .filename - The name of the uploaded file.
    .value - The contents of the uploaded file.

Here's the code!

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    from circuits.web import Server, Controller
    
    
    UPLOAD_FORM = """
    <html>
     <head>
      <title>Upload Form</title>
     </head>
     <body>
      <h1>Upload Form</h1>
      <form method="POST" action="/" enctype="multipart/form-data">
       Description: <input type="text" name="desc"><br>
       <input type="file" name="file">
       <input type="submit" value="Submit">
      </form>
     </body>
    </html>
    """
    
    UPLOADED_FILE = """
    <html>
     <head>
      <title>Uploaded File</title>
     </head>
     <body>
      <h1>Uploaded File</h1>
      <p>
       Filename: %s<br>
       Description: %s
      </p>
      <p><b>File Contents:</b></p>
      <pre>
      %s
      </pre>
     </body>
    </html>
    """
    
    
    class Root(Controller):

        def index(self, file=None, desc=""):
            if file is None:
                return UPLOAD_FORM
            else:
                filename = file.filename
                return UPLOADED_FILE % (file.filename, desc, file.value)
    
    
    (Server(8000) + Root()).run()

circuits.web automatically handles form and file uploads and gives you access
to the uploaded file via arguments to the request handler after they've been
processed by the dispatcher.


How Do I: Integrate with WSGI Applications
------------------------------------------


Integrating with other WSGI Applications is
quite easy to do. Simply add in an instance
of the :class:`~circuits.web.wsgi.Gateway`
component into your circuits.web application.

Example:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    from circuits.web.wsgi import Gateway
    from circuits.web import Controller, Server
    
    
    def foo(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return ["Foo!"]
    
    
    class Root(Controller):
        """App Rot"""
        
        def index(self):
            return "Hello World!"
    
    
    app = Server(("0.0.0.0", 10000))
    Root().register(app)
    Gateway({"/foo": foo}).register(app)
    app.run()

The ``apps`` argument of the :class:`~circuits.web.wsgi.Gateway`
component takes a key/value pair of ``path -> callable``
(*a Python dictionary*) that maps each URI to a given
WSGI callable.


How Do I: Deploy with Apache and mod_wsgi
-----------------------------------------


Here's how to deploy your new Circuits powered Web Application on Apache
using mod_wsgi.

Let's say you have a Web Hosting account with some provider.

- Your Username is: "joblogs"
- Your URL is: http://example.com/~joeblogs/
- Your Docroot is: /home/joeblogs/www/


Configuring Apache
..................


The first step is to add in the following .htaccess file to tell Apache 
hat we want any and all requests to http://example.com/~joeblogs/ to be
served up by our circuits.web application.

Created the .htaccess file in your **Docroot**::
    
    ReWriteEngine On
    ReWriteCond %{REQUEST_FILENAME} !-f
    ReWriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ /~joeblogs/index.wsgi/$1 [QSA,PT,L]


Running your Application with Apache/mod_wsgi
.............................................


The get your Web Application working and deployed on Apache using mod_wsgi,
you need to make a few changes to your code. Based on our Basic Hello World
example earlier, we modify it to the following:

.. code-block:: python
    :linenos:
    
    #!/usr/bin/env python
    
    from circuits.web import Controller
    from circuits.web.wsgi import Application
    
    
    class Root(Controller):
        
        def index(self):
            return "Hello World!"
    
    
    application = Application() + Root()

That's it! To run this, save it as index.wsgi and place it in your Web Root
(public-html or www directory) as per the above guidelines and point your
favorite Web Browser to: http://example.com/~joeblogs/

.. note:: It is recommended that you actually use a reverse proxy
          setup for deploying circuits.web web application so that
          you don't loose the advantages and functionality of using
          an event-driven component architecture in your web apps.
        
          In **production** you should use a load balance and reverse
          proxy combination for best performance.
