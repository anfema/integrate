import os
import inspect
import sys
import fnmatch

from .test import TestCase
from .check import Check


# helper function to load a module from a file
def load_module(module_name, filename):
    if sys.version_info >= (3, 5):
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    elif sys.version_info >= (3, 3):
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader(module_name, filename)
        module = loader.load_module()
        return module
    elif sys.version_info >= (2, 7):
        import imp
        module = imp.load_source(module_name.split('.')[-1], filename)
        return module
    else:
        raise Exception("What version of python are you running?")


class TestRunner(object):

    def __init__(self, verbosity=2, dirs=["."], pattern="*_test.py", checker=Check):
        self.verbosity = verbosity
        self.dirs = dirs
        self.pattern = pattern
        self.checker = checker
        super(TestRunner, self).__init__()

    def _discover(self):
        "Scan directories for possible candidate files"
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
                    if issubclass(cls, TestCase):
                        test_cases.append(cls)
            else:
                print("load failed")

        # Filter out all classes that are superclasses of other classes, as the intention is probably not to
        # run those. This will include the base class TestCase.
        base_classes = {base for test_case in test_cases for base in test_case.__bases__}
        return [test_case for test_case in test_cases if test_case not in base_classes]

    def run(self, only=None):
        "Run discovered tests, may be filtered with only="
        files = self._discover()
        test_cases = self._import(files)

        tests = 0
        skipped = 0
        failed = 0
        exfailed = 0
        if only:
            test_cases = [t for t in test_cases if ".".join([t.__module__, t.__name__]).startswith(only)]
        for test in test_cases:
            num_tests, num_failed, num_exfailed, num_skipped = test(
                verbosity=self.verbosity,
                checker=self.checker
            ).run()
            tests += num_tests
            skipped += num_skipped
            failed += num_failed
            exfailed += num_exfailed

        print("Summary: Ran {} tests, {} succeeded, {} failed ({} expected), {} skipped".format(
            tests,
            tests - skipped - failed,
            failed,
            exfailed,
            skipped
        ))

        return (tests, failed, exfailed, skipped)

    def plan(self, only=None):
        files = self._discover()
        test_cases = self._import(files)
        if only:
            test_cases = [t for t in test_cases if ".".join([t.__module__, t.__name__]).startswith(only)]
        for test in test_cases:
            test(verbosity=self.verbosity, checker=self.checker).plan()
