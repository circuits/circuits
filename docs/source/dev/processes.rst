.. _Issue Tracker: https://github.com/circuits/circuits/issues


Development Processes
=====================


We document all our internal development processes here so you know exactly
how we work and what to expect. If you find any issues or problems please
let us know!


Software Development Life Cycle (SDLC)
--------------------------------------


We employ the use of the `SCRUM Agile Process <http://en.wikipedia.org/wiki/Scrum_(development)>`_
and use our `Issue Tracker`_ to track features, bugs, chores and releases.
If you wish to contribute to circuits, please familiarize yourself with SCRUM
and `GitHub <https://github.com>`_'s Issue Tracker.


Bug Reports
-----------


- New Bug Reports are submitted via:
  https://github.com/circuits/circuits/issues
- Confirmation and Discussion of all New Bug Reports.
- Once confirmed, a new Bug is raised in our `Issue Tracker`_
- An appropriate milestone will be set (*depending on current milestone's schedule and resources*)
- A unit test developed that demonstrates the bug's failure.
- A fix developed that passes the unit test and breaks no others.
- A `New Pull Request <https://github.com/circuits/circuits/compare/>`_ created with the fix.

  This must contains:
  - A new or modified unit test.
  - A patch that fixes the bug ensuring all unit tests pass.
  - The `Change Log <https://github.com/circuits/circuits/tree/master/CHANGES.rst>`_ updated.
  - Appropriate documentation updated.
- The `Pull Request <https://github.com/circuits/circuits/pulls>`_ is reviewed and approved by at least two other developers.


Feature Requests
----------------


- New Feature Requests are submitted via:
  https://github.com/circuits/circuits/issues
- Confirmation and Discussion of all New Feature Requests.
- Once confirmed, a new Feature is raised in our `Issue Tracker`_
- An appropriate milestone will be set (*depending on current milestone's schedule and resources*)
- A unit test developed that demonstrates the new feature.
- The new feature developed that passes the unit test and breaks no others.
- A `New Pull Request <https://github.com/circuits/circuits/compare/>`_ created with the fix.

  This must contains:
  - A new or modified unit test.
  - A patch that implements the new feature ensuring all unit tests pass.
  - The `Change Log <https://github.com/circuits/circuits/tree/master/CHANGES.rst>`_ updated.
  - Appropriate documentation updated.
- The `Pull Request <https://github.com/circuits/circuits/pulls>`_ is reviewed and approved by at least two other developers.


Writing new Code
----------------


- Submit a `New Issue <https://github.com/circuits/circuits/issues/new>`_
- Write your code.
- Use `flake8 <http://pypi.python.org/pypi/flake8>`_ to ensure code quality.
- Run the tests::
      
    $ tox

- Ensure any new or modified code does not break existing unit tests.
- Update any relevant doc strings or documentation.
- Update the `Change Log <https://github.com/circuits/circuits/tree/master/CHANGES.rst>`_ updated.
- Submit a `New Pull Request <https://github.com/circuits/circuits/compare/>`_.


Running the Tests
-----------------


To run the tests you will need the following installed:

- `tox <http://codespeak.net/tox/>`_ installed as well as
- `pytest-cov <http://pypi.python.org/pypi/pytest-cov>`_
- `pytest <http://pytest.org/latest/>`_

All of these can be installed via ``pip``.

Please also ensure that you you have all supported versions of Python
that circuits supports installed in your local environment.

To run the tests::
    
    $ tox
