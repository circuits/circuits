.. _Pivotal Tracker: http://pivotaltracker.com/projects/695621

Development Processes
=====================


We document all our internal development processes here so you know exactly
how we work and what to expect. If you find any issues or problems please
let us know!


Software Development Life Cycle (SDLC)
--------------------------------------


We employ the use of the `SCRUM Agile Process <http://en.wikipedia.org/wiki/Scrum_(development)>`_ and use `Pivotal Tracker`_ to track
our stories, bugs, chores and releases. If you wish to contribute
to circuits, please familiarize yourself with SCRUM and Pivotal Tracker.


Bug Reports
-----------


- New Bug Reports are submitted via:
  http://bitbucket.org/circuits/circuits/issues
- Confirmation and Discussion of all New Bug Reports.
- Once confirmed, a new Bug is raised in `Pivotal Tracker`_ into the Icebox.


Feature Requests
----------------


- New Feature Requests are submitted via:
  http://bitbucket.org/circuits/circuits/issues
- Confirmation and Discussion of all New Feature Requests.
- Once confirmed, a new Feature is raised in `Pivotal Tracker`_ into the Icebox.


Writing new Code
----------------


- Write your code.
- Use `flake8 <http://pypi.python.org/pypi/flake8>`_ to ensure code quality.
- Run the tests::

  $ tox

- Ensure any new or modified code does not break existing unit tests.
- Updated any relevant doc strings or documentation.


Running the Tests
-----------------


To run the tests you will need the following installed:

- `tox <http://codespeak.net/tox/>`_ installed as well as
- `pytest-cov <http://pypi.python.org/pypi/pytest-cov>`_
- `pytest <http://pytest.org/latest/>`_

All of these can be installed via ``easy_install`` or ``pip``.

Please also ensure that you you have all supported versions of Python
that circuits supports installed in your local environment.

To run the tests::
   
   $ tox


