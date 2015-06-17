Adding a circuits namespace package
===================================

*circuits* supports adding python namespace packages.


This is especially useful if a collection of components which solve specific problems
in a generic way for a larger user base exists. This could be provided as subpackage in the circuits namespace.


Creating a *circuits*-subpackage
---------------------

Creating a namespace subpackage of circuits can be achieved in the following way.
Assuming we've got a package which implements the SMTP protocol and should be named *circuits.smtp* it can be added in the following way:

A directory structure has to be added which includes a `circuits/__init__.py` file containing the following statements:

.. code:: python

    """This is the circuits.__init__ for the namespace package circuits.smtp.
    This file should not contain further statements.
    """

    # See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
    try:
        __import__('pkg_resources').declare_namespace(__name__)
    except ImportError:  # pragma: no cover
        from pkgutil import extend_path



You now might define various components in `circuits/smtp/__init__.py`.
Include the path to the origin circuits and to your circuits fork in sys.path and the new *circuits.smtp* is ready to go!


Publish namespace projects on PyPi
----------------------------------
