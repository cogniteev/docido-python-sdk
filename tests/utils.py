import os.path as osp
import sys

import vcr as _vcr

from docido_sdk.toolbox.collections_ext import Configuration

__all__ = [
    'TestCaseMixin',
    'vcr',
]


CASSETTE_LIBRARY_DIR = osp.join(osp.dirname(__file__), 'fixtures/cassettes')


#: instance of :py:class:`vcr.VCR` to be used by all unit-tests
vcr = _vcr.VCR(
    cassette_library_dir=CASSETTE_LIBRARY_DIR,
    record_mode='once',
    path_transformer=_vcr.VCR.ensure_suffix('.yaml'),
    filter_headers=['authorization', 'Cookie'],
)


class TestCaseMixin(object):
    """Unit tests utility mixin class
    """
    @classmethod
    def _test_config(cls):
        """Provides content of .yml file named after the Python module
        where the class extending this class is defined.
        """
        module_path = sys.modules[cls.__module__].__file__
        yaml_path = osp.splitext(module_path)[0] + '.yml'
        return Configuration.from_file(yaml_path)
