
import inspect

def decorate_instance_methods(obj, decorator, includes=None, excludes=None):
    """Decorator instance methods of an object.

    :param obj: Python object whose instance methods have to be decorated
    :param decorator:
      instance method decorator.
      >>> def decorate(name, f):
      >>>   def __wrap(*args, **kwargs)
      >>>     print '--> entering instance method {}'.format(name)
      >>>     eax = f(*args, **kwargs)
      >>>     print '<-- leaving instance method {}'.format(name)

    :param string list includes:
      restrict wrapped instance methods. Default is `None` meaning
      that all instance method are wrapped.
    :param string list excludes:
      used to prevent some instance methods to be wrapped. Default is `None`

    :return: new class that inherits the `clazz` specified in parameter.
    """
    class InstanceMethodDecorator(object):
        def __getattribute__(self, name):
            value = obj.__getattribute__(name)
            if excludes and name in excludes:
                return value
            if includes and name not in includes:
                return value
            if inspect.ismethod(value):
                value = decorator(name, value)
            return value
    return InstanceMethodDecorator()
