.. _Python Standard Library: http://docs.python.org/library/

Requirements and Dependencies
=============================

- circuits has no **required** dependencies beyond the `Python Standard Library`_.
- Python: >= 2.6


Other Optional Dependencies
---------------------------

These dependencies are not strictly required and only add additional
features such as the option for a routes dispatcher for circuits.web
and rendering of component graphs for your application.

- `pydot <http://pypi.python.org/pypi/pydot/>`_
  -- For rendering component graphs of an application.
- `pyinotify <http://pyinotify.sourceforge.net/>`_ is required by the
  :mod:`circuits.io.notify` module for real-time I/O notifications.
- `pytest <http://pytest.org>`_ is required to run the test suite.
- `pytest-cov <http://pypi.python.org/pypi/pytest-cov>`_ is required to
  generate coverage data from running the test suite.
