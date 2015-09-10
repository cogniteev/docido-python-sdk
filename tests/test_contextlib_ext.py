import unittest

from docido_sdk.toolbox.contextlib_ext import restore_dict_kv


class TestRestoreDictKV(unittest.TestCase):
    def test_unknown_key(self):
        d = {'a': 'b'}
        with restore_dict_kv(d, 'UNKNOWN'):
            self.assertEqual(d, {'a': 'b'})
            d['UNKNOWN'] = 'foo'
        self.assertTrue('UNKNOWN' not in d)

    def test_backup_key(self):
        d = {'a': 'b'}
        with restore_dict_kv(d, 'a'):
            self.assertEqual(d, {'a': 'b'})
            d['a'] = 'c'
        self.assertEqual(d, {'a': 'b'})


if __name__ == '__main__':
    unittest.main()
