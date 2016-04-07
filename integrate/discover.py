import os
import importlib
import inspect
import sys
import fnmatch

from .test import TestCase
from .check import Check

# helper function to load a module from a file
def load_module(module_name, filename):
	if sys.version_info >= (3,5):
		import importlib.util
		spec = importlib.util.spec_from_file_location(module_name, filename)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		return module
	else:
		from importlib.machinery import SourceFileLoader
		return SourceFileLoader(module_name, filename).load_module()

class TestRunner(object):

	def __init__(self, verbosity=2, dirs=["."], pattern="*_test.py", checker=Check):
		self.verbosity = verbosity
		self.dirs = dirs
		self.pattern = pattern
		self.checker = checker
		super().__init__()

	def _discover(self):
		"Scan directories for possible candiate files"
		files = []
		for d in self.dirs:
			for dirpath, dirnames, filenames in os.walk(d):
				for file in filenames:
					if file == "__init__.py":
						continue
					if fnmatch.fnmatch(file, self.pattern):
						files.append(os.path.join(dirpath, file))
		return files

	def _import(self, files):
		"Import all candidate files and build a list of test cases"
		test_cases = []
		for file in files:
			module_name = file[:-3].replace('/', '.')
			module = load_module(module_name, file)
			if module:
				members = inspect.getmembers(module, predicate=inspect.isclass)
				for name, cls in members:
					if issubclass(cls, TestCase) and cls != TestCase:
						test_cases.append(cls)
		return test_cases

	def run(self, only=None):
		"Run discovered tests, may be filtered with only="
		files = self._discover()
		test_cases = self._import(files)
		if only:
			test_cases = [t for t in test_cases if ".".join([t.__module__, t.__name__]).startswith(only)]
		for test in test_cases:
			test(verbosity=self.verbosity, checker=self.checker).run()
