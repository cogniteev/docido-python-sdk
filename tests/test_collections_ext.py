import unittest

from docido_sdk.toolbox.collections_ext import nameddict, contextobj


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

    def test_with_statement(self):
        a = {'foo': 'bar'}
        proxy = contextobj(a)

        class MyException(Exception):
            pass

        with self.assertRaises(MyException):
            with proxy:
                proxy['foo'] = 'foobar'
                self.assertEquals(proxy['foo'], 'foobar')
                raise MyException()
        self.assertEquals(proxy['foo'], 'bar')


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
