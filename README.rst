.. _Python Programming Language: http://www.python.org/
.. _#circuits IRC Channel: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _FreeNode IRC Network: http://freenode.net
.. _Python Standard Library: http://docs.python.org/library/
.. _Website: https://bitbucket.org/prologic/circuits/
.. _PyPi Page: http://pypi.python.org/pypi/circuits
.. _Read the Docs: http://readthedocs.org/docs/circuits/en/latest/
.. _MIT License: http://www.opensource.org/licenses/mit-license.php
.. _Create an Issue: https://bitbucket.org/prologic/circuits/issue/new
.. _Mailing List: http://groups.google.com/group/circuits-users
.. _Downloads page: https://bitbucket.org/prologic/circuits/downloads


Overview
--------

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

circuits also includes a lightweight, high performance and scalable
HTTP/WSGI compliant web server as well as various I/O and Networking
components.

To take full advantage of circuits and its architecture, circuits
requires that your application be designed in terms of components
and their interactions (*events*) with each other. An application
written using the circuits application framework is maintainable,
scalable and easy to develop.

circuits' **Loosely Coupled** **Component Architecture** allows for a
high level of **Reuse** and **Scalability**. Components are **Componsable**
and much of the component library that circuits ships with are implemented
as composed components.

- **Documentation**: http://packages.python.org/circuits or `Read the Docs`_.
- **Project website**: https://bitbucket.org/prologic/circuits/
- **PyPI page**: http://pypi.python.org/pypi/circuits


Features
--------

- event driven
- concurrency support
- component archiecture
- asynchronous I/O components
- no required external dependencies
- full featured web framework (circuits.web)
- coroutine based synchronization primitives


Requirements
------------

- circuits has no dependencies beyond the `Python Standard Library`_.
- Python: >= 2.6


Installation
------------

The simplest and recommended way to install circuits is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install circuits

If you do not have pip, you may use easy_install::

    > easy_install circuits

Alternatively, you may download the source package from the
`PyPi Page`_ or the `Downloads page`_ on the
`Website`_; extract it and install using::

    > python setup.py install


License
-------

circuits is licensed under the `MIT License`_.


Feedback
--------

We welcome any questions or feedback about bugs and suggestions on how to
improve circuits. Let us know what you think about circuits. `@pythoncircuits <http://twitter.com/pythoncircuits>`_.

Do you have suggestions for improvement? Then please `Create an Issue`_
with details of what you would like to see. I'll take a look at it and
work with you to either incorporate the idea or find a better solution.


Community
---------

There is also a small community of circuits enthusiasts that you may
find on the `#circuits IRC Channel`_ on the `FreeNode IRC Network`_
and the `Mailing List`_.
