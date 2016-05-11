import os.path as osp

import vcr as _vcr

__all__ = [
    'vcr'
]


CASSETTE_LIBRARY_DIR = osp.join(osp.dirname(__file__), 'fixtures/cassettes')


#: instance of :py:class:`vcr.VCR` to be used by all unit-tests
vcr = _vcr.VCR(
    cassette_library_dir=CASSETTE_LIBRARY_DIR,
    record_mode='once',
    path_transformer=_vcr.VCR.ensure_suffix('.yaml'),
    filter_headers=['authorization', 'Cookie'],
)
