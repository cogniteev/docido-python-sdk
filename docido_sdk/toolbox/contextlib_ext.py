
from contextlib import contextmanager
import copy


@contextmanager
def restore(obj, copy_func=copy.deepcopy):
    """Backup an object in a with context and restore it when leaving
    the scope.

    :param obj: object to backup
    :param copy_func: callbable object used to create an object copy.
    default is `copy.deepcopy`
    """
    backup = copy_func(obj)
    try:
        yield obj
    finally:
        obj = backup
