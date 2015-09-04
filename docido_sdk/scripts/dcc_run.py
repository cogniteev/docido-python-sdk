from .. import loader
from ..env import env
from ..oauth import OAuthToken
from ..core import (
    implements,
    Component,
    ExtensionPoint,
)
from ..crawler import ICrawler
from ..index.config import YamlPullCrawlersIndexingConfig
from ..index.test import LocalKV, LocalDumbIndex
from ..index.processor import (
    Elasticsearch,
    CheckProcessor,
)
from ..index.pipeline import (
    IndexPipelineProvider,
    IndexAPIConfigurationProvider,
)

import logging
import yaml
import pickle
from pickle import PickleError


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

    def _check_pickle(self, tasks):
        return pickle.dumps(tasks)

    def run(self, full=False):
        tokens = oauth_tokens_from_file()
        index_pipeline_provider = env[IndexPipelineProvider]
        for crawler, launches in tokens.iteritems():
            c = [c for c in self.crawlers if c.get_service_name() == crawler]
            if len(c) != 1:
                raise Exception(
                    'unknown crawler for service: {}'.format(crawler)
                )
            c = c[0]
            for launch, oauth in launches.iteritems():
                logger = logging.getLogger(
                    '{crawler}.{launch}'.format(crawler=crawler, launch=launch)
                )
                index_api = index_pipeline_provider.get_index_api(
                    crawler, None, None
                )
                tasks = c.iter_crawl_tasks(index_api, oauth, logger, full)
                try:
                    self._check_pickle(tasks)
                except PickleError as e:
                    raise Exception(
                        'unable to serialize crawl tasks: {}'.format(str(e))
                    )

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
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-i', action='store_true', dest='incremental')
    parser.add_option(
        '-v', '--verbose',
        action='count',
        dest='verbose'
    )
    (options, args) = parser.parse_args()
    verbose = options.verbose if options.verbose is not None else 0
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose > 1:
        logging.level = logging.DEBUG
    logging.basicConfig(level=logging_level)

    loader.load_components(env)
    env[YamlPullCrawlersIndexingConfig]
    env[Elasticsearch]
    env[CheckProcessor]
    env[IndexPipelineProvider]
    env[LocalKV]
    env[LocalDumbIndex]
    runner = env[LocalRunner]
    runner.run(full=not options.incremental)
