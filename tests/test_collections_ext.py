import os
import tempfile
import shutil
import unittest

from docido_sdk.toolbox.collections_ext import (
    Configuration,
    contextobj,
    hashabledict,
    flatten_dict,
    nameddict,
)


class TestContextObj(unittest.TestCase):
    def test_push_n_pop(self):
        a = {'foo': 'bar'}
        p1 = contextobj(a)
        self.assertEquals(p1['foo'], 'bar')
        p1._push()
        self.assertEquals(p1['foo'], 'bar')
        p1['foo'] = 'foobar'
        p1['john'] = 'doe'
        p1._pop()
        self.assertEqual(p1['foo'], 'bar')
        self.assertFalse('john' in p1)

    def test_combined(self):
        proxy = contextobj(nameddict({'foo': 'bar'}))
        proxy['john'] = 'doe'
        self.assertEqual(proxy.john, 'doe')
        with proxy:
            proxy.clear()
            proxy['kikoo'] = 'plop'
            self.assertEqual(proxy.kikoo, 'plop')

    def test_with_statement(self):
        a = {'foo': 'bar'}
        proxy = contextobj(a)

        with proxy:
            proxy['foo'] = 'foobar'
            self.assertEquals(proxy['foo'], 'foobar')
        self.assertEquals(proxy['foo'], 'bar')

    def test_copy_on_push(self):
        proxy = contextobj({'foo': 'bar'})
        self.assertEqual(proxy['foo'], 'bar')
        with proxy:
            self.assertEqual(proxy['foo'], 'bar')
            proxy['foo'] = 'pika'
            self.assertEqual(proxy['foo'], 'pika')
        self.assertEqual(proxy['foo'], 'bar')

    def test_start_from_empty_config(self):
        p = contextobj(nameddict())
        p['foo'] = 'bar'
        with p:
            self.assertEqual(p['foo'], 'bar')
            p['foo'] = 'foobar'
            with p:
                print p.keys()
                p.pop('foo')
            self.assertEqual(p['foo'], 'foobar')
        self.assertEqual(p['foo'], 'bar')

    def test_push_on_unsupported_type(self):
        class A():
            pass
        proxy = contextobj(A())
        with self.assertRaises(NotImplementedError):
            proxy._push()


class TestNamedDict(unittest.TestCase):
    def test_init(self):
        e = nameddict()
        self.assertEqual(len(e), 0)
        e = nameddict([('foo', 'bar'), ('pika', 'lol')])
        self.assertTrue(len(e), e)
        self.assertEqual(e['foo'], 'bar')
        self.assertEqual(e.foo, 'bar')

    def test_add_key(self):
        e = nameddict()
        e['foo'] = 'bar'
        self.assertEqual(e.foo, 'bar')
        e = nameddict()
        e.foo = 'bar'
        self.assertEqual(e['foo'], 'bar')

    def test_del_key(self):
        e = nameddict([('foo', 'bar')])
        self.assertEqual(e.foo, 'bar')
        del e['foo']
        self.assertEqual(len(e), 0)
        with self.assertRaises(AttributeError):
            e.foo

    def test_nested_dict(self):
        data = {
            'foo': {
                'bar': {
                    'pika': 'value'
                }
            },
        }
        e = nameddict(data)
        self.assertEqual(e.foo, {'bar': {'pika': 'value'}})
        self.assertEqual(e.foo.bar, {'pika': 'value'})
        self.assertEqual(e.foo.bar.pika, 'value')

        e['pika'] = {
            'key': 'value'
        }
        self.assertEqual(e.pika, {'key': 'value'})
        self.assertEqual(e.pika.key, 'value')

        e = nameddict()
        e.foo = {'key': 'value'}
        self.assertEqual(e.foo.key, 'value')

    def test_nested_assignment(self):
        """ nested assignment is not supported"""
        e = nameddict()
        with self.assertRaises(AttributeError):
            e.foo.bar = 'pika'

    def test_uppercase_keys(self):
        e = nameddict({'FOO': 'bar'})
        self.assertFalse('foo' in e)
        with self.assertRaises(AttributeError):
            e.foo
        self.assertEqual(e['FOO'], 'bar')
        self.assertEqual(e.FOO, 'bar')


class TestConfiguration(unittest.TestCase):
    def test_env_error(self):
        try:
            tmpdir = tempfile.mkdtemp()
            envvar = 'TestConfigurationSettings'
            os.environ[envvar] = tmpdir
            with self.assertRaises(IOError):
                Configuration.from_env(envvar, None, {})
        finally:
            shutil.rmtree(tmpdir)


class TestFlattenDict(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(flatten_dict({}), {})

    def test_nested_dict(self):
        self.assertEqual(
            flatten_dict({
                'foo': 42,
                'bar': {
                    'foo': 43
                }
            }),
            {
                'foo': 42,
                'bar.foo': 43
            }
        )

    def test_conflict(self):
        self.assertEqual(
            flatten_dict({
                'bar.foo': 42,
                'bar': {
                    'foo': 43
                }
            }),
            {
                'bar.foo': 42,
                'bar.foo.2': 43,
            }
        )

    def test_list(self):
        self.assertEqual(
            flatten_dict({
                'foo': [
                    dict(bar=42),
                    dict(pika='plop'),
                    dict(bar=43),
                ]
            }),
            {
                'foo.0.bar': 42,
                'foo.1.pika': 'plop',
                'foo.2.bar': 43,
            }
        )


class TestHashableDict(unittest.TestCase):
    def test_empty_dict(self):
        the_hash = hash(hashabledict())
        self.assertIsNotNone(the_hash)
        self.assertEqual(the_hash, hash(hashabledict()))

    def test_single_key_dict(self):
        self.assertEqual(
            hash(hashabledict(foo=42)),
            hash(hashabledict(foo=42))
        )
        self.assertNotEqual(
            hash(hashabledict(foo=42)),
            hash(hashabledict(foo=43))
        )

    def test_dict_with_lists(self):
        self.assertIsNotNone(hash(hashabledict({
            'foo': [
                dict(bar=42),
                dict(pika='plop'),
                dict(bar=43),
            ]
        })))

    def test_nested_dict(self):
        self.assertIsNotNone(hash(hashabledict({
            'foo': 42,
            'bar': {
                'foo': 43
            }
        })))

if __name__ == '__main__':
    unittest.main()
