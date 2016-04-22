import inspect
from functools import wraps
from .check import Check


def test(*args, **kwargs):
    def test_wrapper(func):
        @wraps(func)
        def test_decorator(self, check):
            return func(self, check)
        setattr(test_decorator, 'is_test', True)
        for key, value in kwargs.items():
            setattr(test_decorator, key, value)
        return test_decorator
    return test_wrapper


def _test_name(func):
    if func.__doc__:
        return func.__doc__
    else:
        return func.__name__


class DepNode:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.edges = []

    def addEdge(self, node):
        self.edges.append(node)

    @staticmethod
    def dep_resolve(node, resolved, unresolved):
        unresolved.append(node)
        for edge in node.edges:
            if edge not in resolved:
                if edge in unresolved:
                    raise Exception('Circular reference detected: %s -> %s' % (node.name, edge.name))
                DepNode.dep_resolve(edge, resolved, unresolved)
        resolved.append(node)
        unresolved.remove(node)

    @staticmethod
    def dependency_len(node):
        resolved = []
        DepNode.dep_resolve(node, resolved, [])
        return len(resolved)


class TestCase(object):

    def __init__(self, verbosity=2, checker=Check):
        self.verbosity = verbosity
        self.checker = checker
        super().__init__()

    def _solve_dependencies(self, tests):
        # build a dependency tree
        nodes = []
        for name, func in tests:
            node = DepNode(name, func)
            nodes.append(node)

        for node in nodes:
            for dep in getattr(node.func, 'depends', []) + getattr(node.func, 'skip_if_failed', []):
                for n in nodes:
                    if n.name == dep:
                        node.addEdge(n)

        # sort by resolved dep count
        nodes = sorted(nodes, key=lambda node: DepNode.dependency_len(node))

        # flatten the dependency list
        sorted_tests = []
        for node in nodes:
            if len(node.edges) == 0:
                sorted_tests.append((node.name, node.func))
            else:
                resolved = []
                DepNode.dep_resolve(node, resolved, [])
                for n in resolved:
                    skip = False
                    for name, func in sorted_tests:
                        if name == n.name:
                            skip = True
                            break
                    if not skip:
                        sorted_tests.append((n.name, n.func))

        return sorted_tests

    def plan(self):
        # collect tests
        possible_tests = inspect.getmembers(self, predicate=inspect.ismethod)
        tests = []
        max_len = 0
        for name, func in possible_tests:
            if getattr(func, 'is_test', False):
                tests.append((name, func))
                if len(_test_name(func)) > max_len:
                    max_len = len(_test_name(func))
        tests = self._solve_dependencies(tests)

        if self.verbosity > 0:
            print("* Plan for test suite '{}'".format(self.__class__.__doc__))
            for name, func in tests:
                if getattr(func, 'expect_fail', None):
                    print("  - {}".format(name))
                else:
                    print("  - {} (expecting failure)".format(name))

        return [name for name, func in tests]

    def run(self):
        "Run the tests in this test case"
        self.results = {}

        print("* Running test suite '{}'".format(self.__class__.__doc__))
        self.setup_all()

        # collect tests
        possible_tests = inspect.getmembers(self, predicate=inspect.ismethod)
        tests = []
        max_len = 0
        for name, func in possible_tests:
            if getattr(func, 'is_test', False):
                tests.append((name, func))
                if len(_test_name(func)) > max_len:
                    max_len = len(_test_name(func))
        tests = self._solve_dependencies(tests)

        # run tests
        num_skipped = 0
        num_exfail = 0
        for name, func in tests:
            self.results[name] = self.checker()
            print("  - Running {: <{len}}: ".format(
                _test_name(func),
                len=max_len+1
            ), end='', flush=True)

            # tests marked as 'skip' are to be skipped
            if getattr(func, 'skip', False):
                print("[ SKIP ]", flush=True)
                self.results[name].skipped = True

            # tests that have a skip_if_failed need to be
            # skipped if any of their deps failed
            for dep in getattr(func, 'skip_if_failed', []):
                if len(self.results[dep].errors) > 0 \
                   or self.results[dep].skipped:
                    self.results[name].skipped = True
                    if self.verbosity > 0:
                        print("[ SKIP: Dependency ]", flush=True)
                    else:
                        print("[ SKIP ]", flush=True)
                    break

            if self.results[name].skipped:
                num_skipped += 1
                continue

            # tests marked as 'expect_fail' log as expected failures
            if getattr(func, 'expect_fail', None):
                num_exfail += 1

            self.setup_test()
            try:
                func(self.results[name])
            except Exception as e:
                self.results[name].log_error("did raise {}: {}".format(
                    type(e).__name__, e
                ), None)
            self.teardown_test()
            if len(self.results[name].errors) == 0:
                print("[  OK  ]", flush=True)
            else:
                verb = "FAIL"
                if getattr(func, 'expect_fail', None):
                    verb = "EXFAIL"
                if self.verbosity > 0:
                    print("[ {}: {} ]".format(
                        verb,
                        self.results[name].error_message()
                    ), flush=True)
                else:
                    print("[ {} ]".format(verb), flush=True)

        # log summary
        num_errors = 0
        if self.verbosity > 1:
            for name, func in tests:
                if len(self.results[name].errors) == 0:
                    continue
                num_errors += 1

            if num_errors > 0:
                print("\nFailed tests:")
                print("=" * 40 + "\n")
                for name, func in tests:
                    if len(self.results[name].errors) == 0:
                        continue
                    print("-> " + _test_name(func))
                    print("-" * 40)
                    for error in self.results[name].errors:
                        print("".join(error['traceback']))
                        print(error['message'])
                        if error['detail']:
                            print(error['detail'])
                        print()
                        print("-" * 40)
                    print()
            if num_skipped > 0:
                print("Skipped tests:")
                print("=" * 40 + "\n")
                for name, func in tests:
                    if self.results[name].skipped:
                        print("- " + _test_name(func))
                print()
        else:
            for name, func in tests:
                if len(self.results[name].errors) == 0:
                    continue
                num_errors += 1

        self.teardown_all()
        print("Ran {} tests, {} succeeded, {} failed ({} expected), {} skipped".format(
            len(tests),
            len(tests) - num_errors - num_skipped,
            num_errors,
            num_exfail,
            num_skipped
        ))
        print()

        return (len(tests), num_errors, num_exfail, num_skipped)

    def setup_all(self):
        "This function is run at the beginning of the test case"
        # default implementation is empty
        pass

    def teardown_all(self):
        "This function is run at the end of the test case"
        # default implementation is empty
        pass

    def setup_test(self):
        "This function is run before each test in the test case"
        # default implementation is empty
        pass

    def teardown_test(self):
        "This function is run after each test in the test case"
        # default implementation is empty
        pass
