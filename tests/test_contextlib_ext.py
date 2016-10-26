import os
import os.path as osp
import unittest

from docido_sdk.toolbox.contextlib_ext import (
    mkstemp,
    popen,
    pushd,
    restore_dict_kv,
    tempdir,
)


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


class TestTempfile(unittest.TestCase):
    def test_pushd(self):
        cwd = osp.realpath(os.getcwd())
        with tempdir() as path, pushd(path) as ppath:
            path = osp.realpath(path)
            ppath = osp.realpath(ppath)
            cwd_in_context = osp.realpath(os.getcwd())
            self.assertNotEqual(cwd, cwd_in_context)
            self.assertEqual(path, ppath)
            self.assertEqual(path, cwd_in_context)
        self.assertEqual(cwd, osp.realpath(os.getcwd()))
        self.assertFalse(osp.isdir(path))

    def test_pushd_keep_dir(self):
        with tempdir(remove=False) as path:
            self.assertTrue(osp.isdir(path))
        self.assertTrue(osp.isdir(path))

    def test_mkstemp(self):
        with mkstemp() as path:
            self.assertTrue(osp.isfile(path))
        self.assertFalse(osp.isfile(path))

    def test_mkstemp_keep_file(self):
        with mkstemp(remove=False) as path:
            self.assertTrue(osp.isfile(path))
        self.assertTrue(osp.isfile(path))


class TestPopen(unittest.TestCase):
    def test_already_dead(self):
        with popen(['/bin/sleep', '30']) as pid:
            proc_path = '/proc/{}'.format(pid)
            self.assertTrue(osp.isdir(proc_path))


if __name__ == '__main__':
    unittest.main()
