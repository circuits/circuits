.. _Python Programming Language: http://www.python.org/
.. _#circuits IRC Channel: http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4
.. _FreeNode IRC Network: http://freenode.net
.. _Python Standard Library: http://docs.python.org/library/
.. _MIT License: http://www.opensource.org/licenses/mit-license.php
.. _Create an Issue: https://github.com/circuits/circuits/issues/new
.. _Mailing List: http://groups.google.com/group/circuits-users
.. _Website: http://circuitsframework.com/
.. _PyPi: http://pypi.python.org/pypi/circuits
.. _Documentation: http://circuits.readthedocs.org/en/latest/
.. _Downloads: https://github.com/circuits/circuits/releases
.. _Ask a Question: http://stackoverflow.com/questions/ask
.. _Stackoverflow: http://stackoverflow.com/
.. _Google+ Group: https://plus.google.com/communities/107775112577294599973

.. image:: https://travis-ci.com/circuits/circuits.svg
   :target: https://travis-ci.com/circuits/circuits
   :alt: Build Status

.. image:: https://codecov.io/gh/circuits/circuits/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/circuits/circuits
  :alt: Coverage

.. image:: https://badge.waffle.io/circuits/circuits.png?label=ready&title=Ready
   :target: https://waffle.io/circuits/circuits
   :alt: Stories Ready

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

circuits also includes a lightweight, high performance and scalable
HTTP/WSGI compliant web server as well as various I/O and Networking
components.

- `Website`_
- `Downloads`_
- `Documentation`_

Got questions?

- `Ask a Question`_ (Tag it: ``circuits-framework``)


Examples
--------

.. include:: examples/index.rst


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
- Python 2.7, 3.4, 3.5, 3.6
- pypy (the newer the better)


Installation
------------

The simplest and recommended way to install circuits is with pip.
You may install the latest stable release from PyPI with pip::

    $ pip install circuits

If you do not have pip, you may use easy_install::

    $ easy_install circuits

Alternatively, you may download the source package from the
`PyPi`_ or the `Downloads`_ extract it and install using::

    $ python setup.py install


.. note::
    You can install the `development version
    <https://github.com/circuits/circuits/archive/master.zip#egg=circuits-dev>`_
    via ``pip install circuits==dev``.


License
-------

circuits is licensed under the `MIT License`_.


Feedback
--------

We welcome any questions or feedback about bugs and suggestions on how to
improve circuits.

Let us know what you think about circuits. `@pythoncircuits <http://twitter.com/pythoncircuits>`_.

Do you have suggestions for improvement? Then please `Create an Issue`_
with details of what you would like to see. I'll take a look at it and
work with you to either incorporate the idea or find a better solution.


Community
---------

There are also several places you can reach out to the circuits community:

- `Mailing List`_
- `Google+ Group`_
- `#circuits IRC Channel`_ on the `FreeNode IRC Network`_
- `Ask a Question`_ on `Stackoverflow`_ (Tag it: ``circuits-framework``)

----

Disclaimer
----------

Whilst I (James Mills) continue to contribute and maintain the circuits project
I do not represent the interests or business of my employer Facebook Inc. The
contributions I make are of my own free time and have no bearing or relevance
to Facebook Inc.
