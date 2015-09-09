import logging
import os
import os.path as osp
import pickle
from pickle import PickleError

import yaml

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
from ..toolbox.collections_ext import nameddict


class YamlAPIConfigurationProvider(Component):
    implements(IndexAPIConfigurationProvider)

    def get_index_api_conf(self, service, docido_user_id, account_login):
        return {
            'service': service,
            'docido_user_id': docido_user_id,
            'account_login': account_login
        }


def oauth_tokens_from_file(full=True, config=None):
    oauth_path = os.getenv('DOCIDO_CC_RUNS', '.dcc-runs.yml')
    with open(oauth_path, 'r') as oauth_file:
        crawlers = nameddict(yaml.load(oauth_file))
        for crawler, runs in crawlers.iteritems():
            for run, run_config in runs.iteritems():
                run_config.token = OAuthToken(**run_config.token)
                run_config.setdefault('config', config)
                run_config.setdefault('full', full)
        return crawlers


def load_yaml(path):
    if not osp.exists(path) and not osp.isabs(path):
        path = osp.join(osp.dirname(osp.abspath(__file__)), path)
    with open(path, 'r') as istr:
        return nameddict(yaml.load(istr))


class LocalRunner(Component):
    crawlers = ExtensionPoint(ICrawler)

    def _check_pickle(self, tasks):
        return pickle.dumps(tasks)

    def run(self, full=False, config=None):
        crawler_runs = oauth_tokens_from_file(full=full, config=config)
        index_pipeline_provider = env[IndexPipelineProvider]
        for crawler, launches in crawler_runs.iteritems():
            c = [c for c in self.crawlers if c.get_service_name() == crawler]
            if len(c) != 1:
                raise Exception(
                    'unknown crawler for service: {}'.format(crawler)
                )
            c = c[0]
            for launch, launch_config in launches.iteritems():
                logger = logging.getLogger(
                    '{crawler}.{launch}'.format(crawler=crawler, launch=launch)
                )
                with docido_config._push():
                    if launch_config.config is not None:
                        docido_config.clear()
                        docido_config.update(load_yaml(launch_config.config))

                    index_api = index_pipeline_provider.get_index_api(
                        crawler, None, None
                    )
                    tasks = c.iter_crawl_tasks(index_api, launch_config.token,
                                               logger, launch_config.full)
                    try:
                        self._check_pickle(tasks)
                    except PickleError as e:
                        raise Exception(
                            'unable to serialize crawl tasks: {}'.format(
                                str(e)
                            )
                        )

                    def _runtask(task):
                        task(index_api, launch_config.token, logger)

                    def _runtasks(tasks):
                        for t in tasks:
                            t(index_api, launch_config.token, logger)

                    _runtasks(tasks['tasks'])
                    if 'epilogue' in tasks:
                        _runtask(tasks['epilogue'])


def run(*args):
    from optparse import OptionParser

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
        help='set verbosity level'
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
