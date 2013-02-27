.. _Python Programming Language: http://www.python.org/
.. _#circuits IRC Channel: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _FreeNode IRC Network: http://freenode.net
.. _Python Standard Library: http://docs.python.org/library/
.. _Website: https://bitbucket.org/prologic/circuits/
.. _PyPi Page: http://pypi.python.org/pypi/circuits
.. _Read the Docs: http://circuits.readthedocs.org/
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
encourages you to design your application in terms of loosely coupled
components. Circuits has a very powerful message passing system that
enables components to interact with each other via events. Applications
written this way tend to be more maintainable, easier to develop and
scale to complex systems.

circuits' **Loosely Coupled** **Component Architecture** allows for a
high level of **Reuse** and **Scalability**. Simpler components can be
combined together to form Complex Components and provide higher level
functionality and abstraction. Much of the circuits component library is
designed and built this way.

- **Documentation**: http://packages.python.org/circuits or `Read the Docs`_.
- **Project website**: https://bitbucket.org/prologic/circuits/
- **PyPI page**: http://pypi.python.org/pypi/circuits


Features
--------

- event driven
- concurrency support
- component architecture
- asynchronous I/O components
- no required external dependencies
- full featured web framework (circuits.web)
- coroutine based synchronization primitives


Requirements
------------

- circuits has no dependencies beyond the `Python Standard Library`_.


Supported Platforms
-------------------

- Linux, FreeBSD, Mac OS X, Windows
- Python 2.6, 2.7, 3.2, 3.3
- pypy 2.0


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


.. raw:: html
   
   <script type="text/javascript" src="http://www.ohloh.net/p/587962/widgets/project_thin_badge.js"></script>
   
