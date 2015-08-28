import os.path as osp
import shutil
import tempfile
import unittest

from docido_sdk.env import Environment
from docido_sdk.index import (
    IndexAPIConfigurationProvider,
    IndexAPIError,
    IndexPipelineConfig,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
from docido_sdk.index.test import LocalKV
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.test import cleanup_component, cleanup_components


@cleanup_component
class ForcePipeline(Component):
    implements(IndexPipelineConfig)

    def get_pipeline(self):
        return [TEST_ENV[LocalKV]]


@cleanup_component
class ForceConfig(Component):
    implements(IndexAPIConfigurationProvider)

    def get_index_api_conf(self, service, docido_user_id, account_login):
        return {
            'local_storage': {
                'documents': {
                    'path': self.env.temp_dir,
                },
                'kv': {
                    'path': self.env.temp_dir,
                },
            }
        }


def build_env():
    env = Environment()
    env[ForcePipeline]
    env[ForceConfig]
    return env

TEST_ENV = build_env()


class TestLocalKV(unittest.TestCase):
    def kv(self):
        pipeline = TEST_ENV[IndexPipelineProvider]
        return pipeline.get_index_api(None, None, None)

    @classmethod
    def setUpClass(cls):
        TEST_ENV.temp_dir = tempfile.mkdtemp()

    def test_kv(self):
        kv = self.kv()
        key = 'key'
        self.assertIsNone(kv.get_key(key))
        kv.set_key(key, 'value1')
        self.assertEqual(kv.get_key(key), 'value1')
        kv.delete_key(key)
        self.assertIsNone(kv.get_key(key))
        kvs = dict([('key' + str(i), 'value' + str(i)) for i in range(1, 4)])
        for k, v in kvs.iteritems():
            kv.set_key(k, v)
        inserted_kvs = dict(kv.get_kvs())
        self.assertEqual(kvs, inserted_kvs)
        kv.delete_keys()
        self.assertEqual({}, kv.get_kvs())

    def test_key_is_None(self):
        kv = self.kv()
        with self.assertRaises(IndexAPIError):
            kv.get_key(None)
        with self.assertRaises(IndexAPIError):
            kv.set_key(None, 'value1')
        with self.assertRaises(IndexAPIError):
            kv.delete_key(None)

    def test_value_is_None(self):
        kv = self.kv()
        with self.assertRaises(IndexAPIError):
            kv.set_key('key', None)

    @classmethod
    def tearDownClass(cls):
        cleanup_components()
        if osp.isdir(TEST_ENV.temp_dir):
            shutil.rmtree(TEST_ENV.temp_dir)

if __name__ == '__main__':
    unittest.main()
