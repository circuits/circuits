.. highlight:: bash

How to install Circuits
=======================

Circuits can by installed in any number of ways, using setuptools' easy_install
from source or using a binary installer. It's highly recommended you try to
install circuits using setuptools or from source.

Using Setuptools
----------------

To instlal Circuits using setuptools' easy_install:

.. code-block:: bash

	$ easy_install circuits

From Source
-----------

To install CIrcuits from source:

Download Circuits from
 * `PyPi <http://pypi.python.org/pypi/circuits/>`_
 * `Circuits Website <http://trac.softcircuit.com.au/circuits/downloads>`_

Extract archive and Install:

.. code-block:: bash

	$ tar zxvf circuits--xxx.tar.gz
	$ python setup.py install

Installing System Wide
~~~~~~~~~~~~~~~~~~~~~~

The insturctions in the previous section describe how to install circuits in
this way. If you want to change the location, use the ``--prefix`` option.

Installing into your Home Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install circuits in your home directory, use the ``--home=/path/to/home``
option to ``setup.py``. Example:
.. code-block:: bash

	$ python setup.py install --home=$HOME

Installing in Development mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install circuits in development mode, use the ``develop`` command
instead of ``install``. This allows you to easily update/upgrade circuits
and not have to worry about re-installing.

Prerequisites
--------------

* Python 2.5 or greater (''Also works with Python-3.x``)

Setting up setuptools:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
On Windows: 

download http://peak.telecommunity.com/dist/ez_setup.py and then run it from 
the command line.

On UNIX: 

If you have curl or  wget installed you can do this with a single command: 

.. code-block:: bash

	$ curl http://peak.telecommunity.com/dist/ez_setup.py | sudo python

Validate the installation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To check if you installed circuits, type:

.. code-block:: bash
	
	$ python -c "import circuits"

If everything worked, nothing should be displayed.

Installing the development version of Circuits (from source)
------------------------------------------------------------

See `Contributing to Circuits`_

.. _Contributing to Circuits: Contributing.html#installing-the-development-version-of-circuits-from-source
