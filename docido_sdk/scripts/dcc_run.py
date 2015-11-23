from contextlib import contextmanager
import datetime
import logging
from optparse import OptionParser
import os
import pickle
from pickle import PickleError
import sys
import time

import six

from .. import loader
from ..env import env
from ..oauth import OAuthToken
from ..core import (
    implements,
    Component,
    ExtensionPoint,
)
from ..crawler import ICrawler
from ..crawler.errors import Retry
from ..index.config import YamlPullCrawlersIndexingConfig
from ..index.processor import (
    Elasticsearch,
    CheckProcessor,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.config as docido_config
from ..toolbox.collections_ext import Configuration
from ..toolbox.date_ext import timestamp_ms
from ..crawler.tasks import (
    reorg_crawl_tasks,
    split_crawl_tasks,
)


def wait_or_raise(logger, retry_exc, attempt):
    if attempt == retry_exc.max_retries:
        raise retry_exc
    if retry_exc.countdown is not None:
        assert isinstance(retry_exc.countdown, six.integer_types)
        wait_time = retry_exc.countdown
        if wait_time < 0:
            raise (Exception("'countdown' is less than 0"), None,
                   sys.exc_info()[2])
    else:
        assert isinstance(retry_exc.eta, datetime.datetime)
        target_ts = timestamp_ms.feeling_lucky(retry_exc.eta)
        now_ts = timestamp_ms.now()
        wait_time = (target_ts - now_ts) / 1e3
        if wait_time < 0:
            raise Exception("'eta' is in the future"), None, sys.exc_info()[2]
    logger.warn("Retry raised, waiting %s seconds {}".format(wait_time))
    time.sleep(wait_time)


def oauth_tokens_from_file(full=True):
    path = os.environ.get('DOCIDO_DCC_RUNS', '.dcc-runs.yml')
    crawlers = Configuration.from_env('DOCIDO_CC_RUNS', '.dcc-runs.yml',
                                      Configuration())
    for crawler, runs in crawlers.iteritems():
        for run, run_config in runs.iteritems():
            for k in 'config', 'token':
                if k not in run_config:
                    message = ("In file {}: missing config key '{}'"
                               " in '{}/{}' crawl description.")
                    raise Exception(message.format(path, k, crawler, run))
            if 'config' not in run_config:
                raise Exception("Missing 'config' key")
            run_config.token = OAuthToken(**run_config.token)
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
        with docido_config:
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
            tasks, epilogue, concurrency = reorg_crawl_tasks(
                tasks,
                int(config.get('max_concurrent_tasks', 2))
            )
            tasks = split_crawl_tasks(tasks, concurrency)

            def _runtask(task, prev_result):
                attempt = 1
                result = None
                kwargs = dict()
                while True:
                    try:
                        result = task(index_api, config.token,
                                      prev_result, logger, **kwargs)
                        break
                    except Retry as e:
                        try:
                            wait_or_raise(logger, e, attempt)
                        except:
                            logger.exception('Max retries reached')
                            result = e
                            break
                        else:
                            attempt += 1
                            kwargs = e.kwargs
                    except Exception as e:
                        logger.exception('Unexpected exception was raised')
                        result = e
                        break
                return result

            results = []
            for seq in tasks:
                previous_result = None
                for task in seq:
                    previous_result = _runtask(task, previous_result)
                results.append(previous_result)
            if epilogue is not None:
                _runtask(epilogue, results)

    def run_all(self, full=False):
        crawler_runs = oauth_tokens_from_file(full=full)
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
    if args is None:  # pragma: no cover
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


def configure_loggers(verbose):  # pragma: no cover
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


def _prepare_environment(environment):
    environment = environment or env
    loader.load_components(environment)
    from ..index.test import LocalKV, LocalDumbIndex
    components = [
        YamlPullCrawlersIndexingConfig,
        Elasticsearch,
        CheckProcessor,
        IndexPipelineProvider,
        LocalKV,
        LocalDumbIndex,
    ]
    for component in components:
        _ = environment[component]
        del _  # unused
    return env


@contextmanager
def get_crawls_runner(environment=None):
    from docido_sdk.index.pipeline import IndexAPIConfigurationProvider

    class YamlAPIConfigurationProvider(Component):
        implements(IndexAPIConfigurationProvider)

        def get_index_api_conf(self, service, docido_user_id, account_login):
            return {
                'service': service,
                'docido_user_id': docido_user_id,
                'account_login': account_login
            }
    environment = _prepare_environment(environment)
    try:
        yield env[LocalRunner]
    finally:
        YamlAPIConfigurationProvider.unregister()


def run(args=None, environment=None):
    options, args = parse_options(args)
    configure_loggers(options.verbose)
    with get_crawls_runner(environment) as runner:
        runner.run_all(full=not options.incremental)
