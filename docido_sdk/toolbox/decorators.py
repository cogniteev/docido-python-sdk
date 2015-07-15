
import functools

class lazy(object):
    """A lazily-evaluated attribute.

    :since: 1.0
    """

    def __init__(self, fn):
        self.fn = fn
        functools.update_wrapper(self, fn)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fn.__name__ in instance.__dict__:
            return instance.__dict__[self.fn.__name__]
        result = self.fn(instance)
        instance.__dict__[self.fn.__name__] = result
        return result

    def __set__(self, instance, value):
        instance.__dict__[self.fn.__name__] = value

    def __delete__(self, instance):
        del instance.__dict__[self.fn.__name__]

