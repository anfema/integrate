=====================================================
 integrate - Testing framework for integration tests
=====================================================

The usual testing frameworks you can find for Python are so-called unit-testing-frameworks. As this collides with some goals of integration testing this framework was built.

---------
Changelog
---------

1.0.0
=====

- First release, supports Python >= 3.3

1.1.0
=====

- Backport to work on Python 2.7
- If you want to use Python 3 use at least 3.3

1.2.0
=====

- Bugfix: Python 2 issue (Re #4)
- Ignore Test Base classes (Thanks withrocks: https://github.com/withrocks)
- Testrunner.run() now returns stats (Thanks nooploop: https://github.com/nooploop)


---------------------------------------------------------------------
 What's the difference between integration testing and unit-testing?
---------------------------------------------------------------------

In unit testing you should only test the smallest possible thing in your application (or library) and all test should be independent and the ordering of tests is not of particular interest. To make that possible it is very common to stub or mock data models or other external dependencies and only test the functionality of your data transforms. You define fixtures and setup and teardown functions to prepare the environment for a unit test and destroy that environment immediately after running the test.

Integration testing tests the complete system and has no direct influence on the data in the system so naturally the ordering of tests matter and tests may have dependencies (one test creates a DB record which another one modifies, etc.)

As you should test one thing in an unit-test only, you should only use a single assert in a unit test. The default behaviour of most assert methods in unit-testing-frameworks is to raise an exception. This means everything after the failed assert is skipped and the test is marked as failed. In integration-testing you probably want to check multiple things at once and get a detailed error report which checks failed exactly.

----------------------------------------------
 What does this framework better than others?
----------------------------------------------

1. You have full control over which tests run in what order (if you want)
2. You can mark tests as dependent on others, so they will be skipped when a dependency fails
3. You can log as many errors as you want in a single test. Every error saves a stack trace and the error message for further debugging
4. The test runner is very flexible (Your python files that contain the tests do not need to be in python modules)

------------------------------
 How to use it aka Quickstart
------------------------------

1. Install::

	pip install integrate

2. Write a test case class::

	from integrate import TestCase, test

	class Test(TestCase):
		"Simple test case"

		@test(skip_if_failed=["other_test"])
		def simple_test(self, check):
			check.equal(1,2)

		@test()
		def other_test(self, check):
			"Always failing test"
			check.fail("Always fails")

3. Write a test-runner (we assume you put the test case into ``tests/test.py``)::

	#!/usr/bin/env python

	from integrate import TestRunner
	TestRunner(dirs=["tests"], pattern="*.py").run()

4. Make it executable and run it (or run with ``python testrunner.py``)::

	chmod a+x testrunner.py
	./testrunner.py

---------------------
 Short documentation
---------------------

All tests have to be in a class that is derived from ``TestCase``, you may put anything in that class that you want, functions that should be called by the test runner have to be decorated with ``@test()``.

``TestCase`` class
==================

The ``TestCase`` class is the workhorse of the integrate framework. It has some functions you may override in a subclass in addition to adding test functions:

- ``def setup_all(self):``
  This function is run at the beginning of the test case class before any test is started
- ``def teardown_all(self):``
  This function is run at the end of the test case class after all tests have finished
- ``def setup_test(self):``
  This function is run before each test in the test case
- ``def teardown_test(self):``
  This function is run after each test in the test case

You can run the test case class by it's own by calling ``YourTestCase().run()`` or rely on the test runner

There are some interesting initialization parameters:

- ``verbosity``, how verbose the test output should be (min: 0, max: 2, default: 2)
- ``checker``, which ``Check`` subclass to use, usually you will use the default ``Check`` class, but you may extend that to add methods to the ``check`` object all tests receive


``@test`` decorator
===================

All functions that should be picked up by the ``TestCase`` class have to be decorated with ``@test()`` (notice the parentheses!), the decorator has some optional parameters:

- ``skip`` boolean, defaults to ``False``, set to ``True`` to skip a test
- ``skip_if_failed`` list of strings, names of test functions that have to succeed (not fail or be skipped) in order for this function to run, defaults to an empty list
- ``depends`` list of strings, names of test functions that should be run before this function, defaults to an empty list
- ``expect_fail`` boolean, set to true if you expect this test to fail (just for logging purposes)

The test functions have 2 parameters: ``self`` and ``check``, for the description of ``check`` read on.


``Check`` class
===============

All errors that surface in a test should be found and logged by an instance of the ``Check`` class. You may subclass this class to add additional checker functions and insert it into the ``TestCase`` or ``TestRunner`` initializer.

The assertion API looks like the following, if there is a ``message`` parameter it usually is optional and may be left out. User messages are prepended to an error message:

- ``equal(a, b, message=None)``
  Check if two values are equal
- ``not_equal(a, b, message=None)``
  Check if two values are not equal
- ``is_none(a, message=None)``
  Check if a value is None
- ``is_not_none(a, message=None)``
  Check if a value is not None
- ``is_true(a, message=None)``
  Check if a value is True
- ``is_false(a, message=None)``
  Check if a value is False
- ``fail(message)``
  Just log an error message
- ``raises(exception_type, function, *args, **kwargs)``
  Check if a function raises a specified exception type, args and kwargs are forwarded to the function
- ``does_not_raise(function, *args, **kwargs)``
  Check if a function does not raise an exception, args and kwargs are forwarded to the function

All check functions should return ``True`` if the check succeeded and ``False`` if it failed if they don't have to return any other result (like the ``raises`` and ``does_not_raise`` functions which return the result of the function or ``None``)

Exceptions in test functions will still cancel the test function and log the exception to the error log if you don't wrap it with a ``raises()`` call. The traceback of an exception caught by the toplevel will be not of much use though if you can't pinpoint the location based on the exception type. If you just want to catch all exceptions use ``check.raises(Exception, myFunc, "myParam")``

For extending the ``Check`` class there is a, rather small, extension API:

- ``log_error(error, message, detail=None, strip=4)``
  Use this function to add an error to the list, a corresponding stack trace is appended automatically. The ``error`` parameter is a textual one line description of the error, the ``message`` parameter is a user message. Use the ``detail`` parameter to give a detailed error description if needed. Only modify the ``strip`` parameter if your stacktrace gets entries after the error location in the test, by default it strips the last 4 stack frames as these are in the testing framework and just clobber the stack traces.
- ``error_message()``
  Use this for debugging, this function joins all error messages into one string


``TestRunner`` class
====================

The ``TestRunner`` class is the entry point for automatically discovering tests in a project and running them. It has some initialization parameters:

- ``verbosity`` verbosity of test output (min: 0, max: 2, default: 2)
- ``dirs`` list of directories to scan for tests, defaults to current directory. Directories are scanned recursively.
- ``pattern`` file name pattern to search (argument to ``fnmatch``) defaults to the python best practice ``*_test.py``
- ``checker`` the ``Check`` subclass to send to the tests, if you have subclassed the ``Check`` class put your class here, defaults to the unmodified ``Check`` class

To start the tests instanciate the test runner and call the ``run()`` function::

	from integrate import TestRunner
	TestRunner().run()

If you want to run just some tests of your test suite you may either run the tests directly by calling ``run()`` on the ``TestCase`` subclass or by supplying a filter to the ``run()`` function of the test runner like so::

	TestRunner().run(only='special.')

This example would only run tests which have a module name that starts with ``special.`` the module names are generated by replacing all slashes of the python file path with a dot and removing the ``.py`` extension.

A test file that is stored in the path ``special/tests/runme.py`` will get a module name of ``special.tests.runme``.

If you only want to look at what the Test runner would actually do use the ``plan()`` function, this just displays a list of test that would be executed and the order of execution instead of really running the tests. It has the same parameters as the ``run()`` function.
