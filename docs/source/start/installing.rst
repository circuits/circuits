Installing
==========


Installing from a Source Package
--------------------------------
*If you have downloaded a source archive, this applies to you.*


.. code-block:: sh

   $ python setup.py install

For other installation options see:

.. code-block:: sh

   $ python setup.py --help install


Installing from the Development Repository
------------------------------------------
*If you have cloned the source code repository, this applies to you.*


If you have cloned the development repository, it is recommended that you
use setuptools and use the following command:

.. code-block:: sh

   $ python setup.py develop

This will allow you to regularly update your copy of the circuits development
repository by simply performing the following in the circuits working directory:

.. code-block:: sh

   $ hg pull -u

.. note::
   You do not need to reinstall if you have installed with setuptools via
   the circuits repository and used setuptools to install in "develop" mode.
