import copy

import voluptuous
from yamlious import from_dict, merge_dicts
from docido_sdk.index import (
    IndexAPIError,
    IndexAPIProcessor,
    IndexAPIProvider,
    PullCrawlerIndexingConfig,
)
from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
    Interface,
)
from docido_sdk.toolbox.decorators import lazy


__all__ = ['CheckProcessor']


class Check(IndexAPIProcessor):
    """ An index api processor responsible for document and query structure
    checks

    Based on predefined voluptuous Schema, every document will be checked or
    an IndexAPIError will be raised
    """
    def __init__(self, card_schema, query_schema, **kwargs):
        super(Check, self).__init__(**kwargs)
        assert isinstance(card_schema, voluptuous.Schema)
        assert isinstance(query_schema, voluptuous.Schema)
        self.card_schema = card_schema
        self.query_schema = query_schema

    def push_cards(self, cards):
        for c in cards:
            try:
                # add 'attachments' field if missing, otherwise voluptuous
                # yells
                c.setdefault('attachments', [])
                self._check_attachments(c)
                self.card_schema(c)

            except voluptuous.MultipleInvalid as e:
                raise IndexAPIError(e)
        return self._parent.push_cards(cards)

    def _check_attachments(self, card):
        titles = set()
        for attachment in card['attachments']:
            title = attachment['title']
            if title in titles:
                IndexAPIError.build(card).message(
                    "Cannot have 2 attachments with the same 'title'")._raise()
            titles.add(title)


    def search_cards(self, query=None):
        try:
            self.query_schema(query or {})
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return self._parent.search_cards(query)

    def delete_thumbnails(self, query=None):
        try:
            self.query_schema(query)
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return self._parent.delete_thumbnails(query)

    def delete_cards(self, query=None):
        try:
            self.query_schema(query)
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return self._parent.delete_cards(query)


class CheckProcessorSchemaProvider(Interface):
    def card_schema(service):
        pass

    def query_schema(service):
        pass


class CheckProcessor(Component):
    implements(IndexAPIProvider)
    schema_provider = ExtensionPoint(CheckProcessorSchemaProvider, unique=True)

    def get_index_api(self, **config):
        service = config['service']
        card_schema = self.schema_provider.card_schema(service)
        query_schema = self.schema_provider.query_schema(service)
        return Check(card_schema, query_schema, **config)


class DocidoCheckProcessorSchemaProvider(Component):
    implements(CheckProcessorSchemaProvider)
    indexing_config = ExtensionPoint(PullCrawlerIndexingConfig, unique=True)

    def _get_config(self, indexing_config):
        check_processor = indexing_config.get('check_processor', {})
        return check_processor.get('schemas', {})

    @lazy
    def _core_config(self):
        return self._get_config(self.indexing_config.core())

    def _crawler_config(self, service):
        return self._get_config(self.indexing_config.service(service))

    def _get_schema(self, service, type):
        schema, options = from_dict(merge_dicts(
            copy.deepcopy(self._core_config.get(type, {})),
            copy.deepcopy(self._crawler_config(service).get(type, {}))
        ))
        return voluptuous.Schema(schema, **options)

    def card_schema(self, service):
        return self._get_schema(service, 'card')

    def query_schema(self, service):
        return self._get_schema(service, 'query')
