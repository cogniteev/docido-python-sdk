from itertools import repeat
import tempfile
import unittest

from docido_sdk.toolbox.decorators import lazy
from docido_sdk.test import (
    cleanup_component,
    cleanup_components,
)
from docido_sdk.env import Environment
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.index import (
    IndexPipelineConfig,
    IndexAPIConfigurationProvider,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
from docido_sdk.index.test import LocalDumbIndex


@cleanup_component
class ForcePipeline(Component):
    implements(IndexPipelineConfig)

    def get_pipeline(self):
        return [TEST_ENV[LocalDumbIndex]]


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


class TestLocalIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEST_ENV.temp_dir = tempfile.mkdtemp()

    @lazy
    def index(self):
        pipeline = TEST_ENV[IndexPipelineProvider]
        return pipeline.get_index_api(None, None, None)

    def test_push_and_get_card(self):
        card = {
            'id': 12345
        }
        self.index.push_cards(repeat(card, 1))
        self.assertEqual(self.index.search_cards(), [card])

    @classmethod
    def tearDownClass(cls):
        cleanup_components()


if __name__ == '__main___':
    unittest.main()
