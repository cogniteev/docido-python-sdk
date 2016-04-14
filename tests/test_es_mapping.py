import os
import unittest

from elasticsearch import Elasticsearch as _Elasticsearch

from docido_sdk import config

from docido_sdk.index.processor.es_api import ElasticsearchMappingProcessor


class TestESMappingProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config._push()

        config.elasticsearch = {
            'ES_INDEX': 'do_sdk_ut',
            'ES_HOST': os.getenv('ELASTICSEARCH_HOST', 'local.docker:9200'),
            'ES_CARD_TYPE': 'crawl_element',
            'MAPPING': {
                'do_sdk_ut': {
                    'attachments.other_jobtitles': {
                        'properties': {
                            'attachments': {
                                'type': 'nested',
                                'properties': {
                                    'other_jobtitles': {
                                        'index': 'not_analyzed',
                                        'type': 'string'
                                    }
                                }
                            }
                        }
                    },
                    'attachments.other_companies': {
                        'properties': {
                            'attachments': {
                                'type': 'nested', 'properties': {
                                    'other_companies': {
                                        'index': 'not_analyzed',
                                        'type': 'string',
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }

    def test_without_elasticsearch_index(self):
        es = _Elasticsearch(config.elasticsearch.ES_HOST)
        es_index = config.elasticsearch.ES_INDEX
        es_type = config.elasticsearch.ES_CARD_TYPE
        if es.indices.exists(es_index):
            es.indices.delete(es_index)
        self.assertFalse(es.indices.exists(es_index))
        ElasticsearchMappingProcessor(service='a_service')
        self.assertTrue(es.indices.exists(es_index))
        mapping = es.indices.get_mapping(index=es_index, doc_type=es_type)
        self.assertTrue(es_index in mapping)
        mappings = mapping[es_index]['mappings']
        self.assertTrue(es_type in mappings)
        doc_type_mapping = mappings[es_type]
        self.assertIsNotNone(doc_type_mapping)
        self.assertNotEquals(doc_type_mapping, {})

    def test_without_elasticsearch_mapping_config(self):
        try:
            mapping = config.elasticsearch.MAPPING
            config.elasticsearch.pop('MAPPING')
            es = _Elasticsearch(config.elasticsearch.ES_HOST)
            es_index = config.elasticsearch.ES_INDEX
            es_type = config.elasticsearch.ES_CARD_TYPE
            if es.indices.exists(es_index):
                es.indices.delete(es_index)
            ElasticsearchMappingProcessor(service='a_service')
            self.assertTrue(es.indices.exists(es_index))
            mapping = es.indices.get_mapping(index=es_index, doc_type=es_type)
            self.assertFalse(es_index in mapping)
        finally:
            config.elasticsearch.MAPPING = mapping

    @classmethod
    def tearDownClass(cls):
        es_config = config.elasticsearch
        es = _Elasticsearch(es_config.ES_HOST)
        if es.indices.exists(es_config.ES_INDEX):
            try:
                es.indices.delete_mapping(
                    index=es_config.ES_INDEX,
                    doc_type=es_config.ES_CARD_TYPE
                )
            except:
                pass
            es.indices.delete(es_config.ES_INDEX)
        config._pop()


if __name__ == '__main__':
    unittest.main()
