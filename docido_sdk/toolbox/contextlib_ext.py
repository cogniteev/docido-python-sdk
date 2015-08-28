
from contextlib import contextmanager
import copy


@contextmanager
def restore_dict_kv(a_dict, key, copy_func=copy.deepcopy):
    """Backup an object in a with context and restore it when leaving
    the scope.

    :param a_dict:
      associative table
    :param: key
      key whose value has to be backed up
    :param copy_func: callbable object used to create an object copy.
    default is `copy.deepcopy`
    """
    backup = copy_func(a_dict[key])
    try:
        yield
    finally:
        a_dict[key] = backup
