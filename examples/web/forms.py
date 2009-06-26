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
   <a href="http://trac.softcircuit.com.au/circuits/">circuits</a> and it's
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
        return "Hello %s %s<br /><a href=\"/\">Return</a>" % (
                firstName, lastName)

(Server(8000) + Root()).run()
