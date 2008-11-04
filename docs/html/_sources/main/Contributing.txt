Contributing to Circuits
========================

:status: Work in Progress

.. contents::
    :depth: 2

If you want to help out, we want to help you help out! The goal of
this document is to help you get started and answer any questions you
might have.

Installing the Development Version of Circuits (from source)
------------------------------------------------------------

Pre-requisites
~~~~~~~~~~~~~~

#. Python 2.5 or better (http://python.org/download)

#. setuptools_

#. Mercurial_

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _Mercurial: http://www.selenic.com/mercurial/wiki/index.cgi/BinaryPackages

Installing Circuits from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the latest code from the Mercurial respository:

.. code-block:: bash

  $ hg clone http://hg.softcircuit.com.au/projects/circuits/


Tell setuptools to use this version:

.. code-block:: bash

  $ cd circuits
  $ python setup.py develop

Congratulations!  You now have a source installation of Circuits.
Happy Hacking!


Troubleshooting
~~~~~~~~~~~~~~~

*No known issues*

Coding style
------------

Since it's hard to argue with someone who's already written a code style 
document, Circuits follows `PEP 8`_ conventions.

.. _PEP 8: http://www.python.org/peps/pep-0008.html


Testing
-------

Automated unit tests are better than good. They make future growth of the
project possible.

Circuits uses Nose_, which makes testing easy. You can run the
tests just by running `nosetests` or `make tests`.

.. code-block:: bash

  $ cd circuits
  $ make tests

.. _Nose: http://somethingaboutorange.com/mrl/projects/nose/


Documentation
-------------

As mentioned in the `Project Philosophy`_ document, a feature doesn't 
truly exist until it's documented. Tests can serve as good documentation,
because you at least know that they're accurate. But, it's also nice to 
have some information in English.

The Circuits Documentation is available at: http://trac.softcircuit.com.au/circuits/chrome/site/docs/index.html

Please document your own work. It doesn't have to be Shakespeare, but 
the editors don't enjoy writing documentation any more than you do (we'd 
rather be coding) and it's much easier to edit an existing doc than it is
to figure out your code and write something from scratch.

To contribute documentation you can either:

* Write a page in the SandBox_ section of the Circuits
  wiki and request a review of it by submitting a ticket_.
  One of the documentation editors will then pull your
  document into the official documentation, possibly doing
  a bit of editing in the process so that the style and tone
  match the rest of the official documents.

.. _Project Philosophy: http://trac.softcircuit.com.au/circuits/chrome/site/docs/main/Philosophy.html
.. _SandBox: http://trac.softcircuit.com.au/circuits/wiki/SandBox
.. _ticket: http://trac.softcircuit.com.au/circuits/newticket

* Get a copy of the latest source tree, edit the reStructured
  Text source files, and submit patches via tickets on the `Circuits
  Trac`_

.. _TurboGears Trac: http://trac.softcircuit.com.au/circuits/

If you want to work on the docs sources and build the documentation
tree you will also need:

     * Sphinx_

.. _Sphinx: http://sphinx.pocoo.org/

Assuming that you're going to work in a virtualenv called `tg2dev`,
activate the virtualenv:

Get the latest version of the Circuits soruces from the Mercurial
respository:

.. code-block:: bash

  $ hg clone http://hg.softcircuit.com.au/projects/circuits/
  $ cd circuits

Build the documentation tree with:

.. code-block:: bash

  $ cd docs
  $ make html

You can view the docs by pointing your browser at the file::

  docs/html/index.html


Documenting Changes
-------------------

The `Circuits Trac`_ is mostly used for tracking upcoming changes
and tasks required before release of a new version. The changelog_
provides the human readable list of changes.

.. _changelog: http://trac.softcircuit.com.au/circuits/wiki/1.0/ChangeLog
.. _Circuits Trac: http://trac.softcircuit.com.au/circuits/

Updating the changelog right before a release just slows down the
release. Please **update the changelog as you make changes**, and this
is **especially** critical for **backwards incompatibilities**.


How to Submit a Patch
---------------------

Please make sure that you read and follow the `patching guidelines`_.

.. _patching guidelines: http://trac.softcircuit.com.au/circuits/wiki/docs/PatchingGuidelines
