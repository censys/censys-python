import warnings
import functools


class DeprecationDecorator:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                self.message or "Call to deprecated function {}.".format(func.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func(*args, **kwargs)

        return new_func
