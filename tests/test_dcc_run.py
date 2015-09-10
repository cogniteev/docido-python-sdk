from contextlib import contextmanager
from itertools import repeat
import logging
import os
import os.path as osp
import unittest

from docido_sdk.core import implements, Component
from docido_sdk.env import Environment
from docido_sdk.crawler import ICrawler
from docido_sdk.index import IndexAPI
from docido_sdk.oauth import OAuthToken
from docido_sdk.scripts import dcc_run
from docido_sdk.toolbox.contextlib_ext import restore_dict_kv
from docido_sdk.toolbox.collections_ext import Configuration
import docido_sdk.config as docido_config


tasks_counter = 0
epilogue_called = True


def _check_task_parameters(*args):
    assert len(args) == 3
    index, token, logger = args
    assert isinstance(index, IndexAPI)
    assert isinstance(token, OAuthToken)
    assert isinstance(logger, logging.Logger)


def _crawl_task(*args):
    global tasks_counter
    _check_task_parameters(*args)
    tasks_counter += 1


def _epilogue(*args):
    global epilogue_called
    _check_task_parameters(*args)
    epilogue_called = True


class TestDCCRun(unittest.TestCase):
    @classmethod
    def _get_crawler_cls(cls, tasks_count, with_epilogue):
        class MyCrawler(Component):
            implements(ICrawler)

            def get_service_name(self):
                return 'fake-crawler'

            def iter_crawl_tasks(self, index, token, logger, full):
                ret = {
                    'tasks': list(repeat(_crawl_task, tasks_count))
                }
                if with_epilogue:
                    ret['epilogue'] = _epilogue
                return ret
        return MyCrawler

    @contextmanager
    def check_crawl(self, tasks_count, with_epilogue):
        global tasks_counter
        global epilogue_called
        tasks_counter = 0
        epilogue_called = False
        try:
            yield
        finally:
            self.assertEqual(tasks_counter, tasks_count)
            self.assertEqual(epilogue_called, with_epilogue)

    @contextmanager
    def crawler(self, *args, **kwargs):
        c = self._get_crawler_cls(*args, **kwargs)
        try:
            yield c
        finally:
            c.unregister()

    def run_crawl(self, *args, **kwargs):
        with restore_dict_kv(os.environ, 'DOCIDO_CC_RUNS'), \
                docido_config, \
                self.crawler(*args, **kwargs), \
                self.check_crawl(*args, **kwargs):
            config_prefix = osp.splitext(__file__)[0]
            os.environ['DOCIDO_CC_RUNS'] = config_prefix + '-runs.yml'
            config_settings = config_prefix + '-settings.yml'
            docido_config.update(Configuration.from_file(config_settings))
            dcc_run.run([], environment=Environment())

    def test_crawler(self):
        """Start fake crawl"""
        self.run_crawl(tasks_count=5, with_epilogue=False)

    def test_crawler_with_epilogue(self):
        """Start fake incremental crawl"""
        self.run_crawl(tasks_count=5, with_epilogue=True)

if __name__ == '__main__':
    unittest.main()
