.. circuits documentation master file, created by
   sphinx-quickstart on Thu Feb  4 09:44:50 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
Introduction
============

circuits is a **Lightweight** **Event** driven **Framework** for the
`Python Programming Language <http://www.python.org/>`_, with a
strong **Component** Architecture. circuits also includes a lightweight,
high performance and scalable HTTP/WSGI web server
(*with some similar features to* `CherryPy <http://www.cherrypy.org/>`_)
as well as various I/O and Networking components.

circuits has a clean architecture and has no required external dependencies.
It has a small footprint and delivers a powerful set of features for building
large, scalable, maintainable applications and systems. circuits comes with a
suite of standard components that can be quickly utilized to create
applications from a simple tool to a complex distributed web application. 

As a simple demonstration (*in the style of the traditional "Hello World!"*):

:download:`helloworld.py <examples/helloworld.py>`

.. literalinclude:: examples/helloworld.py
   :language: python
   :linenos:

Output:

.. code-block:: bash

   $ python helloworld.py 
   Hello World!

circuits was created by and is primarily maintained by
`James Mills <http://prologic.shortcircuit.net.au/>`_

License
=======

circuits is licensed under the MIT License. See the LICENSE file included
in the distribution or refer to the
`License <http://bitbucket.org/prologic/circuits/wiki/License>`_ wiki page on
the `circuits website <http://bitbucket.org/prologic/circuits/>`_.

Contents
========

.. toctree::
   :maxdepth: 2

   foreword
   features
   gettingstarted
   tutorial
   examples
   circuits.web
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
