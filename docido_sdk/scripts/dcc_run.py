from contextlib import contextmanager
import logging
from optparse import OptionParser
import pickle
from pickle import PickleError
import sys

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

import docido_sdk.config as docido_config
from ..toolbox.collections_ext import Configuration


def oauth_tokens_from_file(full=True, config=None):
    crawlers = Configuration.from_env('DOCIDO_CC_RUNS', '.dcc-runs.yml',
                                      Configuration())
    for crawler, runs in crawlers.iteritems():
        for run, run_config in runs.iteritems():
            run_config.token = OAuthToken(**run_config.token)
            run_config.setdefault('config', config)
            run_config.setdefault('full', full)
    return crawlers


class LocalRunner(Component):
    crawlers = ExtensionPoint(ICrawler)

    def _check_pickle(self, tasks):
        try:
            return pickle.dumps(tasks)
        except PickleError as e:
            raise Exception(
                'unable to serialize crawl tasks: {}'.format(str(e))
            )

    def run(self, logger, config, crawler):
        index_provider = env[IndexPipelineProvider]
        logger.info("starting crawl")
        with docido_config._push():
            if config.config is not None:
                docido_config.clear()
                new_config = Configuration.from_file(config.config)
                docido_config.update(new_config)

            index_api = index_provider.get_index_api(
                self.service, None, None
            )
            tasks = crawler.iter_crawl_tasks(index_api, config.token,
                                             logger, config.full)
            self._check_pickle(tasks)

            def _runtask(task):
                task(index_api, config.token, logger)

            map(_runtask, tasks['tasks'])
            if 'epilogue' in tasks:
                _runtask(tasks['epilogue'])

    def run_all(self, full=False, config=None):
        crawler_runs = oauth_tokens_from_file(full=full, config=config)
        for service, launches in crawler_runs.iteritems():
            self.service = service
            c = [c for c in self.crawlers if c.get_service_name() == service]
            if len(c) != 1:
                raise Exception(
                    'unknown crawler for service: {}'.format(service)
                )
            c = c[0]
            for launch, config in launches.iteritems():
                self.launch = launch
                logger = logging.getLogger(
                    '{service}.{launch}'.format(service=self.service,
                                                launch=self.launch)
                )
                self.run(logger, config, c)


def parse_options(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = OptionParser()
    parser.add_option(
        '-i',
        action='store_true',
        dest='incremental',
        help='trigger incremental crawl'
    )
    parser.add_option(
        '-v', '--verbose',
        action='count',
        dest='verbose',
        help='set verbosity level',
        default=0
    )
    return parser.parse_args(args)


def configure_loggers(verbose):
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose > 1:
        logging.level = logging.DEBUG
    logging.basicConfig(level=logging_level)
    # shut up a bunch of loggers
    for l in [
        'elasticsearch',
        'requests.packages.urllib3.connectionpool',
        'urllib3.connectionpool',
    ]:
        logging.getLogger(l).setLevel(logging.WARNING)


@contextmanager
def get_crawls_runner(environment=None):

    class YamlAPIConfigurationProvider(Component):
        implements(IndexAPIConfigurationProvider)

        def get_index_api_conf(self, service, docido_user_id, account_login):
            return {
                'service': service,
                'docido_user_id': docido_user_id,
                'account_login': account_login
            }
    try:
        environment = environment or env
        loader.load_components(environment)
        from docido_sdk.core import ComponentMeta
        environment[YamlPullCrawlersIndexingConfig]
        environment[Elasticsearch]
        environment[CheckProcessor]
        environment[IndexPipelineProvider]
        environment[LocalKV]
        environment[LocalDumbIndex]
        yield env[LocalRunner]
    finally:
        YamlAPIConfigurationProvider.unregister()


def run(args=None, environment=None):
    options, args = parse_options(args)
    configure_loggers(options.verbose)
    with get_crawls_runner(environment) as runner:
        runner.run_all(full=not options.incremental)
