import os
import unittest

from docido_sdk.toolbox.mongo_ext import (
    KwargsqlToMongo,
    MongoClientPool,
)


class MongoPool(unittest.TestCase):
    MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

    def test_connect_twice(self):
        con1 = MongoClientPool.get(host=self.MONGO_HOST)
        con2 = MongoClientPool.get(host=self.MONGO_HOST)
        self.assertEqual(
            hash(con1),
            hash(con2)
        )
        self.assertEqual(
            con1.admin.command('ping'),
            dict(ok=1.0)
        )

    def test_connect_change_parameters(self):
        con1 = MongoClientPool.get(host=self.MONGO_HOST)
        con2 = MongoClientPool.get(host=self.MONGO_HOST, maxpoolsize=42)
        con3 = MongoClientPool.get(host=self.MONGO_HOST)
        self.assertNotEqual(hash(con1), hash(con2))
        self.assertEqual(hash(con1), hash(con3))
        self.assertEqual(
            con1.admin.command('ping'),
            dict(ok=1.0)
        )
        self.assertEqual(con1.max_pool_size, 100)
        self.assertEqual(con2.max_pool_size, 42)


class KwargsMongoConversion(unittest.TestCase):
    def test_straight_operators(self):
        self.assertEquals(
            KwargsqlToMongo.convert(foo__bar__in=[41, 42]),
            {
                'foo.bar': {
                    '$in': [41, 42],
                },
            },
        )
        self.assertEquals(
            KwargsqlToMongo.convert(foo__bar__exists=42),
            {
                'foo.bar': {
                    '$exists': True,
                },
            },
        )

    def test_compound_and_string_ops(self):
        lhs = KwargsqlToMongo.convert(
            foo__bar__exists=1,
            foo__bar__iendswith='pika+',
            foo='plop',
        )
        self.assertIsInstance(lhs, dict)
        self.assertTrue(len(lhs) == 1)
        self.assertItemsEqual(
            lhs.get('$and'),
            [
                {'foo': 'plop'},
                {'foo.bar': {
                    '$exists': True,
                }},
                {'foo.bar': {
                    '$regex': '^.*pika\+$',
                    '$options': 'i',
                }},
            ],
        )

    def test_no_op(self):
        self.assertEqual(
            KwargsqlToMongo.convert(),
            {}
        )


if __name__ == '__main__':
    unittest.main()
