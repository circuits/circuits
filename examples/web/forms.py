#!/usr/bin/env python
"""Forms

A simple example showing how to deal with data forms.
"""
from circuits.web import Controller, Server


FORM = """
<html>
 <head>
  <title>Basic Form Handling</title>
 </head>
 <body>
  <h1>Basic Form Handling</h1>
  <p>
   Example of using
   <a href="http://circuitsframework.com/">circuits</a> and its
   <b>Web Components</b> to build a simple web application that handles
   some basic form data.
  </p>
  <form action="/save" method="POST">
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
      <td colspan=2">
       <input type="submit" value="Save">
     </td>
     </tr>
   </table>
  </form>
 </body>
</html>"""


class Root(Controller):

    def index(self):
        """Request Handler

        Our index request handler which simply returns a response containing
        the contents of our form to display.
        """

        return FORM

    def save(self, firstName, lastName):
        """Save Request Handler

        Our /save request handler (which our form above points to).
        This handler accepts the same arguments as the fields in the
        form either as positional arguments or keyword arguments.

        We will use the date to pretend we've saved the data and
        tell the user what was saved.
        """

        return "Data Saved. firstName={0:s} lastName={1:s}".format(
            firstName, lastName
        )


app = Server(("0.0.0.0", 8000))
Root().register(app)
app.run()
