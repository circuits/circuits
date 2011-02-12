.. _Python Programming Language: http://www.python.org/
.. _circuits IRC Channel: irc://irc.freenode.net/#circuits
.. _Python Standard Library: http://docs.python.org/library/
.. _circuits Website: https://bitbucket.org/prologic/circuits/
.. _circuits Page on PyPI: http://pypi.python.org/pypi/circuits
.. _MIT License: http://www.opensource.org/licenses/mit-license.php
.. _Create an Issue: https://bitbucket.org/prologic/circuits/issue/new
.. _circuits Mailing List: http://groups.google.com/group/circuits-users
.. _circuits Downloads page: https://bitbucket.org/prologic/circuits/downloads


Overview
--------

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

circuits also includes a lightweight, high performance and scalable
HTTP/WSGI web server as well as various I/O and Networking components.

To take full advantage of circuits and it's architecture, circuits
requires that your application be designed in terms of components
and their interactions (*events*) with each other. An application
written using the circuits application framework is maintainable,
scalable and easy to develop.

The circuits framework has a certain elegance making it a rather
attracting feature. New features are built into the framework with
this in mind and circuits "eats it's own dog food" by having a
feature-rich library of components built atop the core components.

**Documentation**: http://packages.python.org/circuits

**Project website**: https://bitbucket.org/prologic/circuits/

**PyPI page**: http://pypi.python.org/pypi/circuits


Features
--------

- event driven
- concurrency support
- compnoent archiecture
- asynchronous I/O components
- no required external dependencies
- full featured web framework (circuits.web)


Requirements
------------

circuits has no dependencies beyond the `Python Standard Library`_.

Some dependencies should be optionally installed if deployed on a Python-2.5
environment such as `processing <http://pypi.python.org/pypi/processing/>`_
for multiprocessing concurrency support and for JSON support the
`simplejson <http://pypi.python.org/pypi/simplejson/>`_ package.


Installation
------------

The simplest and recommended way to install circuits is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install circuits

If you do not have pip, you may use easy_install::

    > easy_install circuits

Alternatively, you may download the source package from the
`circuits Page on PyPI`_ or the `circuits Downloads page`_ on the
`circuits Website`_; extract it and install using::

    > python setup.py install


License
-------

circuits is licensed under the `MIT License`_.


Feedback
--------

I welcome any questions or feedback about bugs and suggestions on how to 
improve circuits. Let me know what you think about circuits. I am on twitter 
`@therealprologic <http://twitter.com/therealprologic>`_.

Do you have suggestions for improvement? Then please `Create an Issue`_
with details of what you would like to see. I'll take a look at it and
work with you to either incorporate the idea or find a better solution.


Community
---------

There is also a small community of circuits enthusiasts that you may
find on the `circuits IRC Channel`_ and the `circuits Mailing List`_.
