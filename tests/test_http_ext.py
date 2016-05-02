import unittest

import requests

import docido_sdk.config
from docido_sdk.toolbox.http_ext import (
    HTTP_SESSION,
    HttpSessionPreparer,
)
from utils import TestCaseMixin


class SessionPreparerTest(unittest.TestCase, TestCaseMixin):
    def test_rate_limiters_force_config(self):
        session = requests.Session()
        rls_config = self._test_config().http.session.rate_limit
        self._test_rate_limiters(session=session, rls_config=rls_config)

    def test_rate_limiters_default_config(self):
        session = requests.Session()
        test_config = self._test_config()
        with docido_sdk.config:  # temporarly update global config
            docido_sdk.config.http = test_config.http
            self._test_rate_limiters(session=session)

    def _test_rate_limiters(self, session=None, rls_config=None):
        session = session or HTTP_SESSION
        HttpSessionPreparer.mount_rate_limit_adapters(
            session, rls_config=rls_config
        )
        self.assertItemsEqual(
            session.adapters.keys(),
            [
                'http://',
                'https://',
                'https://en.wikipedia.org/wiki/Python_(programming_language)',
                'https://fr.wikipedia.org/wiki/Python_(langage)',
            ]
        )


if __name__ == '__main__':
    unittest.main()
