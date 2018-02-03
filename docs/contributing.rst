=====================
Contributing to Divák
=====================
So you want to contribute back to Divák.

   **Thank you**

This project is released under the permissive BSD license so you aren't
required to contribute modifications.  But you are obviously a person of
excellent taste since you found your way here.  The first thing that you will
want to do is to create a fork of

   https://github.com/dave-shawley/divak-tornado

and clone it to your workstation/laptop/phone/whatever::

   git clone git@github.com:your-org/divak-tornado.git

Then you can move forward with your development.

Development Environment
=======================
This library is primarily developed in Python 3 so start by setting up a new
virtual environment named ``env`` in the root directory.  I'm not usually so
opionated as to tell you what to name things but ``env`` is wired through the
*.gitignore* file and that's what I will be using in examples.  If you put the
environment somewhere else, then that works too but you will have to do a
minor amount of mental gymnastics to follow along::

   python3.6 -mvenv --copies env

Next you want to install the development tools using the *pip-formatted*
requirements file *requires/development.txt*.  This will ensure that you are
using the same versions of development tools that tests will be run with::

   ./env/bin/pip -r requires/development.txt

Before you start writing code, do yourself a big favor and make sure that the
tests pass on your local machine.  They should pass but you are better off
safe than sorry::

   ./env/bin/python setup.py nosetests

If they pass, then it's time to start writing code; otherwise, reach out and
file a github issue with the output of ``pip freeze``, the test output, and
any logs that you have handy.

Development Tasks
=================
Most of the tasks are wired up to be run using *setup.py* so activate the
environment and run **./setup.py ...** to run a utility.  Of course you are
more than welcome to use *nosetests*, *sphinx-build*, and other utilities
directly.

* **setup.py nosetests** will run the test suite.  Add *--with-coverage* to
  generate coverage reports to *build/coverage* as well.
* **setup.py flake8** will run the PEP8 checker
* **setup.py build_sphinx** will build the documentation suite into
  *build/sphinx/html*
* **setup.py bdist_wheel** will build a wheel distribution into the
  *dist* directory

Submitting a PR
===============
Once you have made your changes, its time to submit a pull request against the
upstream repository.  Just go through the following checklist before you
create the PR since the integrated CI will fail unless you do:

1. ensure that all of the tests are passing
2. ensure that any new code or branches are covered by tests -- I aim for 100%
   test coverage on lines and branches
3. describe your changes in the *Next Release* section of *docs/changelog.rst*
4. push your changes to your fork and issue the PR

Once again, thank you very much for taking the time to contribute back.
