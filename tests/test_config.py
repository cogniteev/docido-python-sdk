import os
import tempfile
import shutil
import sys
import unittest

from docido_sdk.toolbox.contextlib_ext import restore_dict_kv


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.__has_module = False
        if 'docido_sdk.config' in sys.modules:
            self.__has_module = True
            self.__prev_module = sys.modules.pop('docido_sdk.config')

    def tearDown(self):
        sys.modules.pop('docido_sdk.config', None)
        if self.__has_module:
            sys.modules['docido_sdk_config'] = self.__prev_module

    def test_config_file_is_dir(self):
        temp_dir = tempfile.mkdtemp()
        with restore_dict_kv(os.environ, 'DOCIDO_CONFIG'):
            try:
                os.environ['DOCIDO_CONFIG'] = temp_dir
                with self.assertRaises(IOError):
                    import docido_sdk.config
                    docido_sdk.config.get('foo')  # Prevent PEP8 F401
            finally:
                shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
