import copy

from peak.util.proxies import ObjectWrapper


class nameddict(dict):
    """ Provides dictionary whose keys are accessible via the property
    syntax: `obj.key`
    """
    def __init__(self, *args, **kwargs):
        super(nameddict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.__namify(self.__dict__)

    def __namify(self, a_dict):
        for key in a_dict.keys():
            if isinstance(a_dict[key], dict):
                a_dict[key] = nameddict(a_dict[key])

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = nameddict(value)
        super(nameddict, self).__setitem__(key, value)

    def __setattr__(self, key, value):
        if key != '__dict__' and isinstance(value, dict):
            value = nameddict(value)
        super(nameddict, self).__setattr__(key, value)


class contextobj(ObjectWrapper):
    """ Proxy a Python object, and provides a stack where copies of the
    wrapped object can be manipulated with `_push` and `_pop`
    member functions.

    `contextobj` can also be used in a Python with-statement.

        >>> o = contextobj(dict())
        >>> with o:
        >>>     o['foo'] = 'bar'
        >>> # the dict has been rollbacked: it is empty again
    """
    __obj_stack = None

    def __init__(self, *args, **kwargs):
        super(contextobj, self).__init__(*args, **kwargs)
        self.__obj_stack = []

    def _push(self):
        self.__obj_stack.append(self.__subject__)
        self.__subject__ = copy.deepcopy(self.__subject__)
        return self

    def _pop(self):
        self.__subject__ = self.__obj_stack.pop()
        return self

    def __enter__(self):
        self._push()

    def __exit__(self, type, value, traceback):
        self._pop()
