import errno
import os
import os.path as osp
import sys

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from . toolbox.collections_ext import nameddict, contextobj


class Configuration(nameddict):
    @classmethod
    def from_file(cls, path):
        if not osp.exists(path) and not osp.isabs(path):
            path = osp.join(osp.dirname(osp.abspath(__file__)), path)
        with open(path, 'r') as istr:
            return Configuration(yaml.load(istr, Loader=Loader))

try:
    config = Configuration.from_file(
        os.getenv('DOCIDO_CONFIG', 'settings.yml')
    )
except IOError as e:
    # Issue happened while loading settings.yml
    if e.errno == errno.ENOENT:
        # Ignore issue only if file was not found
        config = {}
    else:
        raise e

sys.modules[__name__] = contextobj(config)
# This module is now the configuration object itself.
