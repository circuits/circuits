Installing
==========

If you have not installed circuits via the the
`setuptools <http://pypi.python.org/pypi/setuptools>`_ easy_install tool,
then the following installation instructions will apply to you. Either
you've downloaded a source package or cloned the development repository.

Installing from a Source Package
--------------------------------

.. code-block:: sh

   $ python setup.py install

For other installation options see:

.. code-block:: sh

   $ python setup.py --help install

Installing from the Development Repository
------------------------------------------

If you have cloned the development repository, it is recommended that you
use setuptools and use the following command:

.. code-block:: sh

   $ python setup.py build develop

**NB:** The "build" command is required when installing from the development
repository (*build creates the version file which is built dynamically*).

This will allow you to regularly update your copy of the circuits development
repository by simply performing the following in the circuits working directory:

.. code-block:: sh

   $ hg pull -u

**NB**: You do not need to reinstall if you have installed with setuptools via
the circuits repository and used setuptools to install in "develop" mode.
