from elasticsearch import Elasticsearch as _Elasticsearch

from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.index import (
    IndexAPIProcessor,
    IndexAPIProvider,
)
import docido_sdk.config as docido_config

__all__ = ['Elasticsearch']


class ElasticsearchProcessor(IndexAPIProcessor):
    """ Main Elasticsearch entry point

    Every sent card or thumbnail will get indexed in the user's associated
    index.

    Also provide convenience method for documents search and deletion
    """

    def __init__(self, **config):
        super(ElasticsearchProcessor, self).__init__(**config)
        es_config = docido_config.elasticsearch
        self.__es_index = es_config.ES_INDEX
        self.__es_store_index = es_config.ES_STORE_INDEX
        self.__card_type = es_config.ES_CARD_TYPE
        self.__store_type = es_config.ES_STORE_TYPE
        self.__routing = config.get('elasticsearch', {}).get('routing')
        self.__es = _Elasticsearch(
            es_config.ES_HOST,
            **es_config.get('connection_params', {})
        )
        self.__es_store = _Elasticsearch(
            es_config.ES_STORE_HOST,
            **es_config.get('connection_params', {})
        )

    def ping(self):
        return self.__es.ping() and self.__es_store.ping()

    def search_cards(self, query):
        generated_results = 0
        batch_size = 10
        offset = 0
        body = {
            'body': query,
            'index': self.__es_index,
            'doc_type': self.__card_type,
            'size': batch_size,
            'from_': offset,
        }
        if self.__routing:
            body['routing'] = self.__routing
        search_results = self.__es.search(**body)

        while generated_results != search_results['hits']['total']:
            for hit in search_results['hits']['hits']:
                generated_results += 1
                yield hit['_source']

            offset += batch_size
            body['from_'] = offset
            search_results = self.__es.search(**body)

    def __delete_es_docs(self, body, es, index, doc_type):
        query = {
            'body': body,
            'index': index,
            'doc_type': doc_type,
        }
        if self.__routing:
            query['routing'] = self.__routing
        es.delete_by_query(**query)

    def delete_cards(self, query):
        return self.__delete_es_docs(
            query,
            self.__es,
            self.__es_index,
            self.__card_type
        )

    def delete_thumbnails(self, query):
        return self.__delete_es_docs(
            query,
            self.__es_store,
            self.__es_store_index,
            self.__store_type
        )

    def __push_es_docs(self, docs, es, index, doc_type):
        body = []
        error_docs = []

        for doc in docs:
            action = {
                'index': {
                    '_index': index,
                    '_type': doc_type
                }
            }
            body.append(action)
            body.append(doc)
        params = {
            'body': body,
            'refresh': True,
        }
        if self.__routing:
            params['routing'] = self.__routing
        results = es.bulk(**params)
        if results['errors']:
            for index, item in enumerate(results['items']):
                if item['create']['status'] not in [200, 201]:
                    error_docs.append(
                        {
                            'card': docs[index],
                            'status': item['create']['status'],
                            'id': docs[index]['id']
                            if 'id' in docs[index] else None,
                            'error': item['create']['error'],
                        }
                    )
        return error_docs

    def push_cards(self, cards):
        return self.__push_es_docs(
            cards,
            self.__es,
            self.__es_index,
            self.__card_type
        )

    def push_thumbnails(self, thumbnails):
        return self.__push_es_docs(
            thumbnails,
            self.__es_store,
            self.__es_store_index,
            self.__store_type
        )


class Elasticsearch(Component):
    implements(IndexAPIProvider)

    def get_index_api(self, **config):
        return ElasticsearchProcessor(**config)