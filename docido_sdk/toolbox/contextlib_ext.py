import copy
import os
import os.path as osp
import shutil
import signal
import subprocess
import tempfile

from .compat import contextlib


@contextlib.contextmanager
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
    exists = False
    if key in a_dict:
        backup = copy_func(a_dict[key])
        exists = True
    try:
        yield
    finally:
        if exists:
            a_dict[key] = backup
        else:
            a_dict.pop(key, None)


@contextlib.contextmanager
def unregister_component(component):
    try:
        component.unregister()
        yield component
    finally:
        component.register()


@contextlib.contextmanager
def tempdir(*args, **kwargs):
    remove = kwargs.pop('remove', True)
    path = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        if remove:
            shutil.rmtree(path)


@contextlib.contextmanager
def pushd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def mkstemp(*args, **kwargs):
    remove = kwargs.pop('remove', True)
    fd, path = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    try:
        yield path
    finally:
        if remove and osp.exists(path):
            os.remove(path)


@contextlib.contextmanager
def popen(*args, **kwargs):
    """Run a process in background in a `with` context. Parameters given
    to this function are passed to `subprocess.Popen`. Process is kill
    when exiting the context.
    """
    process = subprocess.Popen(*args, **kwargs)
    try:
        yield process.pid
    finally:
        os.kill(process.pid, signal.SIGTERM)
        os.waitpid(process.pid, 0)
