How To Guides
=============


These "How To" guides will steer you in the right direction for common
aspects of modern web applications and website design.


How do I...


Use a Templating Engine
-----------------------


circuits.web tries to stay out of your way as much as possible and doesn't
impose any restrictions on what external libraries and tools you can use
throughout your web application or website. As such you can use any template
language/engine you wish.


Using Mako
..........


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
            output_encoding="utf-8")
    
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


Integrate with a Database
-------------------------


.. todo:: Write about this ...


Use WebSockets
--------------


.. todo:: Write about this ...


Build a Simple Form
-------------------


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


Upload a File
-------------


You can easily handle File Uploads as well using the same techniques as above.
Basically the "name" you give your <input> tag of type="file" will get passed
as the Keyword Argument to your Request Handler. It has the following two
attributes:
    
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


Integrate with WSGI Applications
--------------------------------


.. todo:: Write about this ...


Deploy with Apache and mod_wsgi
-------------------------------


Here's how to deploy your new Circuits powered Web Application on Apache
using mod_wsgi.

Let's say you have a Web Hosting account with some provider.

Your Username is: "joblogs"
Your URL is: http://example.com/~joeblogs/
Your Docroot is: /home/joeblogs/www/


Configuring Apache
..................


The first step is to add in the following .htaccess file to tell Apache 
hat we want any and all requests to http://example.com/~joeblogs/ to be
served up by our circuits.web application.

Created the .htaccess file in your **Docroot**:
    
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
