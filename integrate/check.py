import traceback


class Check(object):

    def __init__(self):
        self.errors = []
        self.skipped = False
        super().__init__()

    def log_error(self, error, message, detail=None, strip=4):
        "Add an error message and optional user message to the error list"
        if message:
            msg = message + ": " + error
        else:
            msg = error

        self.errors.append({
            'message': msg,
            'traceback': traceback.format_stack()[:-strip],
        })

    def error_message(self):
        "Get a single error message string with all errors joined"
        return ", ".join([e['message'] for e in self.errors])

    def equal(self, a, b, message=None):
        "Check if two values are equal"
        if a != b:
            self.log_error("{} != {}".format(str(a), str(b)), message)

    def not_equal(self, a, b, message=None):
        "Check if two values are not equal"
        if a == b:
            self.log_error("{} == {}".format(str(a), str(b)), message)

    def is_none(self, a, message=None):
        "Check if a value is None"
        if a is not None:
            self.log_error("{} is not None".format(str(a)), message)

    def is_not_none(self, a, message=None):
        "Check if a value is not None"
        if a is None:
            self.log_error("{} is None".format(str(a)), message)

    def is_true(self, a, message=None):
        "Check if a value is True"
        if not a:
            self.log_error("{} is False".format(str(a)), message)

    def is_false(self, a, message=None):
        "Check if a value is False"
        if a:
            self.log_error("{} is True".format(str(a)), message)

    def fail(self, message):
        "Just log an error message"
        self.log_error(message, None)

    def raises(self, exception_type, function, *args, **kwargs):
        """
            Check if a function raises a specified exception type,
            *args and **kwargs are forwarded to the function
        """
        try:
            result = function(*args, **kwargs)
            self.log_error("{} did not throw exception {}".format(
                function.__name__,
                exception_type.__name__
            ), None)
            return result
        except Exception as e:
            if type(e) != exception_type:
                self.log_error("{} did raise {}: {}".format(
                    function.__name__,
                    type(e).__name__, e
                ), None)

    def does_not_raise(self, function, *args, **kwargs):
        """
            Check if a function does not raise an exception,
            *args and **kwargs are forwarded to the function
        """
        try:
            return function(*args, **kwargs)
        except Exception as e:
            self.log_error("{} did raise {}: {}".format(
                function.__name__,
                type(e).__name__, e
            ), None)
