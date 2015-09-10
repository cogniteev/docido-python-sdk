import copy
import unittest

import docido_sdk.config as docido_config
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.toolbox.decorators import lazy
from docido_sdk.env import Environment
from docido_sdk.index.config import YamlPullCrawlersIndexingConfig
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.index.processor as processor
from docido_sdk.index.test import LocalDumbIndex
from docido_sdk.index import IndexAPIConfigurationProvider, IndexAPIError

from docido_sdk.test import (
    cleanup_component,
    cleanup_components,
)

TEST_CRAWLER_NAME = 'check-processor-test'
TEST_CONFIG = {
    'pull_crawlers': {
        'crawlers': {
            TEST_CRAWLER_NAME: {
                'indexing': {
                    'schemas': {
                        'card': {
                            'foo': basestring
                        },
                    },
                },
            },
        },
        'indexing': {
            'pipeline': [
                'CheckProcessor',
                'LocalDumbIndex',
            ],
            'check_processor': {
                'schemas': {
                    'query': {
                        'content': {
                            'query': 'object'
                        },
                        'options': {
                            'required': True,
                            'extra': True
                        }
                    },
                    'card': {
                        'kind': {
                            'test': {
                                'options': {
                                    'extra': True,
                                    'required': True
                                },
                                'content': {
                                    'id': unicode,
                                    'kind': unicode
                                }
                            }
                        },
                        'default': {
                            'options': {
                                'extra': True,
                                'required': True,
                            },
                            'content': {
                                'id': 'str',
                                'title': 'str',
                                'description': 'str',
                                'date': {
                                    'All': [
                                        'int',
                                        {
                                            'Range': {
                                                'min': 0,
                                            },
                                        },
                                    ],
                                },
                                'kind': 'str',
                                'author': {
                                    'nested': {
                                        'name': 'str',
                                    }
                                },
                                'attachments': [
                                    {
                                        'title': 'str',
                                        'origin_id': 'str',
                                        'type': 'str',
                                        'description': 'str',
                                    }
                                ],
                            },
                        },
                    },
                },
            },
        }
    }
}


@cleanup_component
class DumbIndexAPIConfiguration(Component):
    implements(IndexAPIConfigurationProvider)

    def get_index_api_conf(self, service, docido_user_id, account_login):
        return {
            'service': service,
            'docido_user_id': docido_user_id,
            'account_login': account_login,
        }


class TestCheckProcessor(unittest.TestCase):
    VALID_CARD = {
        'id': '12345',
        'title': 'title1',
        'description': 'description1',
        'date': 12345,
        'kind': 'kind1',
        'author': {
            'name': 'author.name1',
        },
        'attachments': [],
    }

    @classmethod
    def setUpClass(cls):
        docido_config._push().update(TEST_CONFIG)
        cls.env = Environment()
        cls.env[IndexPipelineProvider]
        cls.env[LocalDumbIndex]
        cls.env[YamlPullCrawlersIndexingConfig]
        cls.env[processor.CheckProcessor]
        cls.env[DumbIndexAPIConfiguration]

    @classmethod
    def tearDownClass(cls):
        docido_config._pop()
        cleanup_components()
        YamlPullCrawlersIndexingConfig.unregister()

    @lazy
    def index(self):
        index_builder = self.env[IndexPipelineProvider]
        return index_builder.get_index_api(
            TEST_CRAWLER_NAME, 'user2', 'account3'
        )

    def test_push_valid_document(self):
        self.index.push_cards([self.VALID_CARD])
        self.assertEqual(
            [self.VALID_CARD],
            self.index.search_cards({'query': {'match_all': {}}})
        )

    def test_push_extra_field(self):
        card = copy.deepcopy(self.VALID_CARD)
        self.index.push_cards([card])
        self.assertEqual(
            [card],
            self.index.search_cards({'query': {'match_all': {}}})
        )

    def test_push_invalid_field_type(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['description'] = 12345
        with self.assertRaises(IndexAPIError):
            self.index.push_cards([card])

    def test_push_without_attachments_field(self):
        card = copy.deepcopy(self.VALID_CARD)
        card.pop('attachments')
        self.index.push_cards([card])

    def test_push_one_attachment(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'].append({
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        })
        self.index.push_cards([card])

    def test_push_other_kind(self):
        self.index.push_cards([{'id': u'my_test_id', 'kind': u'test'}])

    def test_push_without_kind(self):
        card = copy.deepcopy(self.VALID_CARD)
        del card['kind']
        with self.assertRaises(IndexAPIError):
            self.index.push_cards([card])

    def test_push_three_attachments(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'] = [{
            'title': 'title' + str(i),
            'origin_id': 'origin_id' + str(i),
            'type': 'type' + str(i),
            'description': 'description' + str(i),
        } for i in range(1, 4)]
        self.index.push_cards([card])

    def test_push_invalid_attachment(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'].append({
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        })
        card['attachments'].append({
            'title': 'title2',
            # missing origin_id field
            'type': 'type2',
            'description': 'description2',
        })
        with self.assertRaises(IndexAPIError):
            self.index.push_cards([card])

    def test_attachments_with_same_name(self):
        card = copy.deepcopy(self.VALID_CARD)
        attachment = {
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        }
        card['attachments'].append(attachment)
        card['attachments'].append(attachment)
        with self.assertRaises(IndexAPIError):
            self.index.push_cards([card])

    def test_search_invalid_query(self):
        with self.assertRaises(IndexAPIError):
            self.index.search_cards({})

    def test_delete_thumbnails_invalid_query(self):
        with self.assertRaises(IndexAPIError):
            self.index.delete_thumbnails({})

    def test_delete_thumbnails(self):
        with self.assertRaises(NotImplementedError):
            self.index.delete_thumbnails({'query': {'match_all': {}}})

    def test_delete_cards(self):
        with self.assertRaises(NotImplementedError):
            self.index.delete_cards({'query': {'match_all': {}}})

    def test_delete_cards_invalid_query(self):
        with self.assertRaises(IndexAPIError):
            self.index.delete_cards({})

if __name__ == '__main__':
    unittest.main()
