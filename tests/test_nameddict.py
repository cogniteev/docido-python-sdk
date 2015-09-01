import unittest

from docido_sdk.toolbox.collections_ext import nameddict


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


if __name__ == '__main__':
    unittest.main()
