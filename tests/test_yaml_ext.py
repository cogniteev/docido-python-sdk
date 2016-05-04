import os
from StringIO import StringIO
import unittest


import yaml
try:
    from yaml import CLoader as Loader
except ImportError:  # pragma: no cover
    from yaml import Loader

from docido_sdk.toolbox.yaml_ext import load_all_yaml_constructors

load_all_yaml_constructors()


class TestYamlExt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['DOCIDO_SDK_YAML_EXT_UT'] = '42'
        os.environ.pop('DOCIDO_SDK_YAML_MISSING', None)

    @classmethod
    def tearDownClass(cls):
        os.environ.pop('DOCIDO_SDK_YAML_EXT_UT')

    def test_missing_mandatory_env(self):
        with self.assertRaises(KeyError) as exc:
            self._get_var_env('DOCIDO_SDK_YAML_MISSING')
        self.assertEqual(
            (u'DOCIDO_SDK_YAML_MISSING',),
            exc.exception.args
        )

    def test_get_mandatory_env(self):
        self.assertEqual(
            '42',
            self._get_var_env('DOCIDO_SDK_YAML_EXT_UT')
        )

    def test_get_var_with_default_value(self):
        self.assertEqual(
            '42',
            self._get_var_env('DOCIDO_SDK_YAML_EXT_UT:=43')
        )

    def test_get_default_value(self):
        self.assertEqual(
            '44',
            self._get_var_env('DOCIDO_SDK_YAML_MISSING:=44')
        )

    def _get_var_env(self, expr):
        yaml_str = 'foo: !env ' + expr
        config = yaml.load(StringIO(yaml_str), Loader=Loader)
        return config['foo']


if __name__ == '__main__':
    unittest.main()
