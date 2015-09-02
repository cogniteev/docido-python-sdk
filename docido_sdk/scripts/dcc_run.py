from ..env import env

from ..oauth import OAuthToken

import logging

from .. import loader

from ..index.processor import (
    Elasticsearch,
    CheckProcessor,
)

from ..index.test import LocalKV, LocalDumbIndex

from .. import config as docido_config

from ..core import (
    implements,
    Component,
    ExtensionPoint,
)

from ..index.config import YamlPullCrawlersIndexingConfig

from ..index import IndexAPIProvider

from ..index.pipeline import (
    IndexPipelineProvider,
    IndexAPIConfigurationProvider,
    IndexPipelineConfig,
)

from ..crawler import ICrawler

import yaml


class YamlAPIConfigurationProvider(Component):
    implements(IndexAPIConfigurationProvider)

    def get_index_api_conf(self, service, docido_user_id, account_login):
        return {
            'service': service,
            'docido_user_id': docido_user_id,
            'account_login': account_login
        }


def oauth_tokens_from_file():
    import os
    oauth_path = os.getenv('DOCIDO_TOKENS', '.oauth_token.yml')
    with open(oauth_path, 'r') as oauth_file:
        oauth_settings = yaml.load(oauth_file)
        tokens = {}
        for crawler_name, launches in oauth_settings.iteritems():
            tokens[crawler_name] = {
                k: OAuthToken(**v)
                for k, v in launches.iteritems()
            }
        return tokens


class LocalRunner(Component):
    crawlers = ExtensionPoint(ICrawler)

    def run(self):
        tokens = oauth_tokens_from_file()
        index_pipeline_provider = env[IndexPipelineProvider]
        for crawler, launches in tokens.iteritems():
            c = filter(lambda c: c.get_service_name() == crawler, self.crawlers)
            if len(c) != 1:
                raise Exception('unknown crawler for service: {}'.format(crawler))
            c = c[0]
            for launch, oauth in launches.iteritems():
                logger = logging.getLogger(
                    '{crawler}.{launch}'.format(crawler=crawler, launch=launch)
                )
                index_api = index_pipeline_provider.get_index_api(
                    crawler, None, None
                )
                Full = True # TODO parse it
                tasks = c.iter_crawl_tasks(index_api, oauth, logger, Full)

                def _runtask(task):
                    task(index_api, oauth, logger)

                def _runtasks(tasks):
                    for t in tasks:
                        t(index_api, oauth, logger)

                if type(tasks) == tuple:
                    _runtasks(tasks[0])
                    _runtask(tasks[1])
                else:
                    _runtasks(tasks)


def run(*args):
    loader.load_components(env)
    env[YamlPullCrawlersIndexingConfig]
    env[Elasticsearch]
    env[CheckProcessor]
    env[IndexPipelineProvider]
    env[LocalKV]
    env[LocalDumbIndex]
    runner = env[LocalRunner]
    runner.run()

if __name__ == '__main__':
    run()
