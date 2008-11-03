Contributing to TurboGears 2
============================

:status: Official

.. contents::
    :depth: 2

If you want to help out, we want to help you help out! The goal of
this document is to help you get started and answer any questions you
might have. The `Project Philosophy`_ document has a more high-level
view, whereas this document is nuts-and-bolts. The `TurboGears team`_
page lists who is responsible for what.

.. _Project Philosophy: http://docs.turbogears.org/1.0/Philosophy
.. _TurboGears team: http://docs.turbogears.org/TurboGearsTeam


Installing the Development Version of Turbogears 2 (from source)
----------------------------------------------------------------

Pre-requisites
~~~~~~~~~~~~~~

#. Python 2.4 or 2.5 (http://python.org/download)

   * Make sure that your Python installation includes the `sqlite`
     extension (some \*BSDs keep it in a separate package).  If
     you're running Python 2.5 you can test for `sqlite` with::

       $ python -c "import sqlite3"

     or try::

       $ python -c "import pysqlite2"

     with Python 2.4.

   * For RPM-based systems you will also need ``python-devel`` and
     ``python-xml`` packages.

   * On `ubuntu` you will need ``python-dev`` and ``python-setuptools``.
#. setuptools_ (run http://peak.telecommunity.com/dist/ez_setup.py from
   any directory)

#. Subversion_

#. Mercurial_

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _Subversion: http://subversion.tigris.org/getting.html
.. _Mercurial: http://www.selenic.com/mercurial/wiki/index.cgi/BinaryPackages

We recommend working in a `virtual environment`_ so that any existing
packages will not interfere with your installation, and so that you
don't upgrade any Python libraries that your system needs.

.. _virtual environment: DownloadInstall.html#setting-up-a-virtual-environment


Installing Pylons from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming that you're going to work in a virtualenv called `tg2dev`,
activate the virtualenv:

.. code-block:: bash

  $ cd tg2dev
  $ source bin/activate

`(tg2dev)` will be prefixed to your prompt to indicate that the
`tg2dev` virtualenv is activated.

Clone the latest Pylons code:

.. code-block:: bash

  (tg2dev)$ hg clone http://pylonshq.com/hg/pylons-dev Pylons

Tell setuptools to use this version:

.. code-block:: bash

  (tg2dev)$ cd Pylons
  (tg2dev)$ python setup.py develop

Installing TurboGears 2 from Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TurboGears 2 is composed of 3 packages.

Check out the latest code from the subversion respositories:

.. code-block:: bash

  (tg2dev)$ cd ..
  (tg2dev)$ svn co http://svn.turbogears.org/projects/tg.devtools/trunk tgdev
  (tg2dev)$ svn co http://svn.turbogears.org/trunk tg2
  (tg2dev)$ svn co http://tgtools.googlecode.com/svn/projects/tg.ext.repoze.who/trunk tg.ext.repoze.who

* tgdev is a set of tools, paster command plugins to create default
  template, admin interface, and migrations.
* tg2 package is TurboGears 2 core.
* tg.ext.repoze.who is an extension for tg2 that aims to provide an
  API compliant implementation of the old tg1 identity framework.

Again, tell setuptools to use these versions.

* tg.ext.repoze.who:

.. code-block:: bash

  (tg2dev)$ cd tg.ext.repoze.who
  (tg2dev)$ easy_install Paste
  (tg2dev)$ easy_install zope.interface
  (tg2dev)$ python setup.py develop

* TurboGears 2 server:

.. code-block:: bash

  (tg2dev)$ cd ..
  (tg2dev)$ cd tg2
  (tg2dev)$ easy_install PasteScript==dev
  (tg2dev)$ easy_install genshi
  (tg2dev)$ python setup.py develop

* TurboGears 2 developer tools:

.. code-block:: bash

  (tg2dev)$ cd ..
  (tg2dev)$ cd tgdev
  (tg2dev)$ python setup.py develop

Congratulations!  You now have a source installation of TurboGears 2.
Happy Hacking!

.. note:: if you have installed old dependency packages, you could remove 
   them from {python_path}/site-packages/easy-install.pth


Troubleshooting
~~~~~~~~~~~~~~~

It is possible (but not likely) you might see a few other error
messages.  Here are the correct ways to fix the dependency problems so
things will install properly.

* If you get an error about ``ObjectDispatchController`` this means
  your Pylons installation is out-of-date. Make sure it's fresh (``hg
  pull -u`` or ``hg pull`` followed by ``hg update`` -- alternatively you
  can create a brand new Pylons branch in a new directory with ``hg
  clone``).

* When installing on Mac OSX, if you get an error mentioning ``No local
  packages or download links found for RuleDispatch``, you can try the
  solution posted to the `ToscaWidgets discussion list`_ which advises
  downloading it directly:

.. code-block:: bash

    (tg2dev)$ sudo easy_install -U -f http://toscawidgets.org/download/wo_speedups/ RuleDispatch

.. _ToscaWidgets discussion list: http://groups.google.com/group/toscawidgets-discuss/browse_thread/thread/cb6778810e96585d

* If you get the following error when starting a project with ``paster
  serve``::

    AttributeError: 'WSGIRequest' object has no attribute 'accept_language'

  update your Pylons checkout with ``hg update`` and try again.


Coding style
------------

Since it's hard to argue with someone who's already written a code style 
document, TurboGears 2 follows `PEP 8`_ conventions.

To ensure that files in the TurboGears source code repository have proper 
line-endings, you must configure your Subversion client. Please see
the `patching guidelines`_ for details.

.. _PEP 8: http://www.python.org/peps/pep-0008.html


Testing
-------

Automated unit tests are better than good. They make future growth of the
project possible.

TurboGears 2 uses Nose_, which makes testing easy. You can run the
tests in each of the source directories just by running `nosetests`.
For example, to run the test on the TG2 server:

.. code-block:: bash

  (tg2dev)$ cd tg2
  (tg2dev)$ nosetests

.. _Nose: http://somethingaboutorange.com/mrl/projects/nose/

Default options for `nosetests` can often be found in the
`[nosetests]` section of `setup.cfg` and additional options can be
passed on the command line.  See the Nose_ documentation for details.

For TG2 projects, the ``tg.testutil`` package includes some utility
functions and classes that make you're life easier as you're trying to
test.


Documentation
-------------

As mentioned in the `Project Philosophy`_ document, a feature doesn't 
truly exist until it's documented. Tests can serve as good documentation,
because you at least know that they're accurate. But, it's also nice to 
have some information in English.

There are two kinds of docs, and both have their useful place:

**API reference**

    A modified epydoc_ (which includes links to the source) is used to
    generate API docs for the website. It's not very taxing at all to add
    these doc strings as you work on the code. See the
    `API reference for version 1.0 <1.0/API>`_ here.

.. _epydoc: http://epydoc.sourceforge.net/

.. TODO: Is epydoc still going to be used for the API, or just Sphinx autodoc?


**Manual**

    The TurboGears 2 documentation is online at
    http://turbogears.org/2.0/docs/

Please document your own work. It doesn't have to be Shakespeare, but 
the editors don't enjoy writing documentation any more than you do (we'd 
rather be coding) and it's much easier to edit an existing doc than it is
to figure out your code and write something from scratch.

To contribute documentation you can either:

* Write a page in the RoughDocs_ section of the TurboGears
  documentation wiki and request a review of it on the
  `turbogears-docs`_ discussion list.  One of the documentation
  editors will then pull your document into the official
  documentation, possibly doing a bit of editing in the process so
  that the style and tone match the rest of the official documents.
  Please see the TG1 `guidelines for contributing documentation`_ for
  pointers on documentation format and style.

.. _RoughDocs: http://docs.turbogears.org/2.0/RoughDocs
.. _turbogears-docs: http://groups.google.ca/group/turbogears-docs
.. _guidelines for contributing documentation: http://docs.turbogears.org/DocHelp

* Check out a copy of the documentation tree, edit the reStructured
  Text source files, and submit patches via tickets on the `TurboGears
  Trac`_

.. _TurboGears Trac: http://trac.turbogears.org/

If you want to work on the docs sources and build the documentation
tree you will also need:

     * Sphinx_
     * `pysvn extension`_

.. _Sphinx: http://sphinx.pocoo.org/
.. _pysvn extension: http://pysvn.tigris.org/project_downloads.html

`pysvn` is a Python extension that comes in source or binary kits to
match your OS, Python version, and Subversion version.  Please see the
`pysvn extension`_ downloads page for details and follow the
instructions there to install the appropriate version.

Assuming that you're going to work in a virtualenv called `tg2dev`,
activate the virtualenv:

.. code-block:: bash

  $ cd tg2dev
  $ source bin/activate

`(tg2dev)` will be prefixed to your prompt to indicate that the
`tg2dev` virtualenv is activated.

Check out the latest version of the docs soruces from the subversion
respositories:

.. code-block:: bash

  (tg2dev)$ svn co http://svn.turbogears.org/docs

Build the documentation tree with:

.. code-block:: bash

  (tg2dev)$ cd docs/2.0/docs
  (tg2dev)$ make html

You can view the docs by pointing your browser at the file::

  docs/2.0/docs/_build/html/index.html


Documenting Changes
-------------------

The `TurboGears Trac`_ is mostly used for tracking upcoming changes
and tasks required before release of a new version. The changelog_
provides the human readable list of changes.

.. _changelog: http://trac.turbogears.org/wiki/2.0/changelog

Updating the changelog right before a release just slows down the
release. Please **update the changelog as you make changes**, and this
is **especially** critical for **backwards incompatibilities**.


How to Submit a Patch
---------------------

Please make sure that you read and follow the `patching guidelines`_.

.. _patching guidelines: http://docs.turbogears.org/patching_guidelines
