import unittest

import requests
from requests.adapters import HTTPAdapter

from docido_sdk.toolbox.rate_limits import (
    RateLimiter,
    RLRequestAdapter,
)
from utils import TestCaseMixin


class RamKV:
    def __init__(self):
        self._kv = dict()

    def get_kv(self, key):
        return self._kv.get(key)

    def set_kv(self, key, value):
        self._kv[key] = value


class TestRateLimiter(unittest.TestCase, TestCaseMixin):
    def test_one_rule_no_persistence(self):
        name = 'ut'
        config = self._test_config()
        config[name].pop('persistence')
        rate_limiter = RateLimiter.get(name, config=config, user='ut')
        for i in range(5):
            self.assertEqual(0, rate_limiter())
        wait_time = rate_limiter(waits=False)
        self.assertLess(0.9, wait_time)
        self.assertGreater(1.1, wait_time)

    def test_single_rate_limit(self):
        self._single_rate_limit()

    def test_single_rate_limit_runtime(self):
        self._single_rate_limit(runtime=True)

    def test_single_rate_limit_loaded_data(self):
        name = 'ut'
        config = self._test_config()
        index = RamKV()
        index.set_kv('rl:docido:ut-user:ut', '1462177808756|5')
        rate_limiter = RateLimiter.get(name, config=config, user='ut-user',
                                       persistence_kwargs=dict(index=index))
        for i in range(1, 6):
            self.assertEqual(0, rate_limiter())
            self.assertEqual(str(i),
                             index._kv['rl:docido:ut-user:ut'].split('|')[1])
        wait_time = rate_limiter(waits=False)
        self.assertLess(0.9, wait_time)
        self.assertGreater(1.1, wait_time)

    def test_multiple_rate_limits(self):
        self._multiple_rate_limits()

    def test_multiple_rate_limits_runtime(self):
        self._multiple_rate_limits(runtime=True)

    def test_session_adapter(self):
        session = requests.Session()
        adapter = RLRequestAdapter('wikipedia_python',
                                   config=self._test_config(),
                                   application='docido_sdk',
                                   base_adapter=HTTPAdapter())
        session.mount('https://de.wikipedia.org', adapter)
        session.mount('https://en.wikipedia.org', adapter)
        session.mount('https://fr.wikipedia.org', adapter)
        urls = [
            'https://de.wikipedia.org/wiki/Python_(Programmiersprache)',
            'https://en.wikipedia.org/wiki/Python_(programming_language)',
            'https://fr.wikipedia.org/wiki/Python_(langage)',
        ]
        for url in urls:
            resp = session.get(url, params=dict(service='service42'))
            self.assertEqual(resp.status_code, 200)
        adapter.close()  # for coverage purpose

    def test_global_config(self):
        self.assertIsInstance(RateLimiter.get_configs(), dict)

    @classmethod
    def _runtime_expr(cls, runtime):
        """Evaluate `runtime` argument of 2 test scenarii"""
        context = dict(user='ut-user')
        if runtime:
            call_kwargs = dict(context=context)
            ctor_kwargs = dict()
        else:
            call_kwargs = dict()
            ctor_kwargs = context
        return ctor_kwargs, call_kwargs

    def _single_rate_limit(self, runtime=False):
        name = 'ut'
        config = self._test_config()
        index = RamKV()
        ctor_kwargs, call_kwargs = self._runtime_expr(runtime)
        rate_limiter = RateLimiter.get(name, config=config,
                                       persistence_kwargs=dict(index=index),
                                       **ctor_kwargs)
        for i in range(1, 6):
            self.assertEqual(0, rate_limiter(**call_kwargs))
            self.assertEqual(str(i),
                             index._kv['rl:docido:ut-user:ut'].split('|')[1])
        wait_time = rate_limiter(waits=False, **call_kwargs)
        self.assertLess(0.9, wait_time)
        self.assertGreater(1.1, wait_time)

    def _multiple_rate_limits(self, runtime=False):
        name = 'ut-multi'
        key = 'rl:docido:192.168.0.1:ut-user:ut-multi'
        config = self._test_config()
        index = RamKV()
        ctor_kwargs, call_kwargs = self._runtime_expr(runtime)
        rate_limiter = RateLimiter.get(name, config=config,
                                       persistence_kwargs=dict(index=index),
                                       **ctor_kwargs)
        for i in range(1, 3):
            self.assertEqual(0, rate_limiter(**call_kwargs))
            self.assertEqual(str(i), index._kv[key].split('|')[1])
        wait_time = rate_limiter(waits=False, **call_kwargs)
        self.assertLess(0.9, wait_time)
        self.assertGreater(1.1, wait_time)


if __name__ == '__main__':
    unittest.main()
